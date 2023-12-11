import asyncio
import enum
import json
import re
from dataclasses import dataclass
from typing import Any, Optional, cast

import aiohttp
import httpx

from aioWiserHeatAPI.helpers.extra_config import _WiserExtraConfig

from . import _LOGGER
from .const import (
    REST_TIMEOUT,
    WISERHUBDOMAIN,
    WISERHUBSCHEDULES,
    WiserUnitsEnum,
)
from .exceptions import (
    WiserExtraConfigError,
    WiserHubAuthenticationError,
    WiserHubConnectionError,
    WiserHubRESTError,
)


@dataclass
class WiserAPIParams:
    passive_mode_increment = 0.5
    stored_manual_target_temperature_alt_source = "current"


# Connection info class
class _WiserConnectionInfo(object):
    def __init__(self):
        self.host = None
        self.secret = None
        self.port = None
        self.units = WiserUnitsEnum.metric
        self.extra_config_file = None
        self.enable_automations = False


# Enums
class WiserRestActionEnum(enum.Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


class _WiserRestController(object):
    """
    Class to handle getting data from and sending commands to a wiser hub
    """

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: Optional[float] = REST_TIMEOUT,
        wiser_connection_info: Optional[_WiserConnectionInfo] = None,
    ):
        self._wiser_connection_info = wiser_connection_info
        self._api_parameters = WiserAPIParams()

        self._timeout = timeout  # aiohttp.ClientTimeout(total=timeout)
        self._hub_name = None
        self._extra_config_file = None
        self._extra_config: _WiserExtraConfig = None

    async def _do_hub_action(
        self,
        action: WiserRestActionEnum,
        url: str,
        data: dict = None,
        raise_for_endpoint_error: bool = True,
    ):
        """
        Send patch update to hub and raise errors if fails
        param url: url of hub rest api endpoint
        param patchData: json object containing command and values to set
        return: boolean
        """

        url = url.format(
            self._wiser_connection_info.host,
            self._wiser_connection_info.port,
        )

        kwargs = {
            "headers": {
                "SECRET": self._wiser_connection_info.secret,
                "Content-Type": "application/json;charset=UTF-8",
                "Connection": "close",
            }
        }

        if data is not None:
            # print(data)
            kwargs["json"] = data
        if self._timeout is not None:
            kwargs["timeout"] = self._timeout

        try:
            async with httpx.AsyncClient() as client:
                response = await getattr(client, action.value)(
                    url,
                    **kwargs,
                )

                if response.status_code >= 400:
                    self._process_nok_response(
                        response, url, data, raise_for_endpoint_error
                    )
                else:
                    content = await response.aread()
                    if len(content) > 0:
                        response = content.decode("utf-8", "ignore").encode(
                            "utf-8"
                        )
                        return json.loads(response)
                    else:
                        return {}
                return {}

        except httpx.TimeoutException as ex:
            raise WiserHubConnectionError(
                f"Connection timeout trying to communicate with Wiser Hub {self._wiser_connection_info.host} for url {url}. Error is {ex}"
            ) from ex
        except httpx.NetworkError as ex:
            raise WiserHubConnectionError(
                f"Connection error trying to communicate with Wiser Hub {self._wiser_connection_info.host} for url {url}. Error is {ex}"
            ) from ex

    def _process_nok_response(
        self,
        response: aiohttp.ClientResponse,
        url: str,
        data: dict,
        raise_for_endpoint_error: bool = True,
    ):
        if response.status_code == 401:
            raise WiserHubAuthenticationError(
                f"Error authenticating to Wiser Hub {self._wiser_connection_info.host}.  Check your secret key"
            )
        elif response.status_code == 404 and raise_for_endpoint_error:
            raise WiserHubRESTError(
                f"Rest endpoint not found on Wiser Hub {self._wiser_connection_info.host} for url {url}"
            )
        elif response.status_code == 408:
            raise WiserHubConnectionError(
                f"Connection timed out trying to communicate with Wiser Hub {self._wiser_connection_info.host} for url {url}"
            )
        elif raise_for_endpoint_error:
            raise WiserHubRESTError(
                f"Unknown error communicating with Wiser Hub {self._wiser_connection_info.host} for url {url} with data {data}.  Error code is: {response.status_code}"
            )

    async def _get_hub_data(
        self, url: str, raise_for_endpoint_error: bool = True
    ):
        """Get data from hub"""
        return await self._do_hub_action(
            WiserRestActionEnum.GET,
            url,
            raise_for_endpoint_error=raise_for_endpoint_error,
        )

    async def _get_extra_config_data(self):
        # Load extra config file

        if self._extra_config_file:
            try:
                self._extra_config = _WiserExtraConfig(
                    self._extra_config_file, self._hub_name.lower()
                )
                await self._extra_config.async_load_config()
            except WiserExtraConfigError as ex:
                _LOGGER.error(
                    "Your config file is corrupted and needs to be fixed to maintain all the functionality of this integration."
                )
                self._extra_config = None

    async def _send_command(
        self,
        url: str,
        command_data: dict,
        method: WiserRestActionEnum = WiserRestActionEnum.PATCH,
    ):
        """
        Send control command to hub and raise errors if fails
        param url: url of hub rest api endpoint
        param patchData: json object containing command and values to set
        return: boolean
        """
        url = WISERHUBDOMAIN + url
        _LOGGER.debug(
            "Sending command to url: {} with parameters {}".format(
                url, command_data
            )
        )

        return await self._do_hub_action(method, url, command_data)

    async def _do_schedule_action(
        self, action: WiserRestActionEnum, url: str, schedule_data: dict = None
    ):
        """
        Perform schedule action to hub and raise errors if fails
        param url: url of hub rest api endpoint
        param patchData: json object containing schedule values to set
        return: boolean
        """
        url = WISERHUBSCHEDULES + url
        _LOGGER.debug(
            "Actioning schedule to url: {} with action {} and data {}".format(
                url, action.value, schedule_data
            )
        )
        return await self._do_hub_action(action, url, schedule_data)

    async def _send_schedule_command(
        self,
        action: str,
        schedule_data: dict,
        id: int = 0,
        schedule_type: str = None,
    ) -> bool:
        """
        Send schedule data to Wiser Hub
        param schedule_data: json schedule data
        param id: schedule id
        return: boolen - true = success, false = failed
        """
        if action == "UPDATE":
            result = await self._do_schedule_action(
                WiserRestActionEnum.PATCH,
                "{}/{}".format(schedule_type, id),
                schedule_data,
            )

        elif action == "CREATE":
            result = await self._do_schedule_action(
                WiserRestActionEnum.POST,
                "Assign",
                schedule_data,
            )

        elif action == "ASSIGN":
            result = await self._do_schedule_action(
                WiserRestActionEnum.PATCH,
                "Assign",
                schedule_data,
            )

        elif action == "DELETE":
            result = await self._do_schedule_action(
                WiserRestActionEnum.DELETE,
                "{}/{}".format(schedule_type, id),
                schedule_data,
            )
        return result
