from . import _LOGGER

from .const import (
    REST_TIMEOUT,
    WISERHUBDOMAIN,
    WISERHUBSCHEDULES,
    WiserUnitsEnum,
)

from .exceptions import (
    WiserHubAuthenticationError,
    WiserHubConnectionError,
    WiserHubRESTError,
)

import asyncio
import aiohttp
import enum

from typing import Any, Optional, cast

# Connection info class
class _WiserConnectionInfo(object):
    def __init(self):
        self.host = None
        self.secret = None
        self.port = None
        self.units = WiserUnitsEnum.metric


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

        if not session:
            session = aiohttp.ClientSession()
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)

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

        kwargs = {
            "headers": {
                "SECRET": self._wiser_connection_info.secret,
                "Content-Type": "application/json;charset=UTF-8",
            }
        }

        if data is not None:
            # print(data)
            kwargs["json"] = data
        if self._timeout is not None:
            kwargs["timeout"] = self._timeout

        try:
            response = cast(
                aiohttp.ClientResponse,
                await getattr(self._session, action.value)(
                    url.format(
                        self._wiser_connection_info.host,
                        self._wiser_connection_info.port,
                    ),
                    **kwargs,
                ),
            )

            if not response.ok:
                self._process_nok_response(response, raise_for_endpoint_error)
            else:
                #    if action == WiserRestActionEnum.GET:
                if len(await response.text()) > 0:
                    # response = re.sub(rb'[^\x20-\x7F]+', b'', response.content.iter_any())
                    return await response.json()
                else:
                    return {}
            return {}

        except asyncio.TimeoutError as ex:
            raise WiserHubConnectionError(
                f"Connection timeout trying to communicate with Wiser Hub {self._wiser_connection_info.host}.  Error is {ex}"
            )
        except aiohttp.ClientResponseError as ex:
            raise WiserHubConnectionError(
                f"Response error trying to communicate with Wiser Hub {self._wiser_connection_info.host}.  Error is {ex}"
            )
        except aiohttp.ClientConnectorError as ex:
            raise WiserHubConnectionError(
                f"Connection error trying to communicate with Wiser Hub {self._wiser_connection_info.host}.  Error is {ex}"
            )

    def _process_nok_response(
        self, response: aiohttp.ClientResponse, raise_for_endpoint_error: bool = True
    ):
        if response.status == 401:
            raise WiserHubAuthenticationError(
                f"Error authenticating to Wiser Hub {self._wiser_connection_info.host}.  Check your secret key"
            )
        elif response.status == 404 and raise_for_endpoint_error:
            raise WiserHubRESTError(
                f"Rest endpoint not found on Wiser Hub {self._wiser_connection_info.host}"
            )
        elif response.status == 408:
            raise WiserHubConnectionError(
                f"Connection timed out trying to communicate with Wiser Hub {self._wiser_connection_info.host}"
            )
        elif raise_for_endpoint_error:
            self._session.close()
            raise WiserHubRESTError(
                f"Unknown error getting communicating with Wiser Hub {self._wiser_connection_info.host}.  Error code is: {response.status}"
            )
        else:
            print("Error of the Unknown kind!")

    async def _get_hub_data(self, url: str, raise_for_endpoint_error: bool = True):
        """Get data from hub"""
        return await self._do_hub_action(
            WiserRestActionEnum.GET,
            url,
            raise_for_endpoint_error=raise_for_endpoint_error,
        )

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
            "Sending command to url: {} with parameters {}".format(url, command_data)
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
        self, action: str, schedule_data: dict, id: int = 0, schedule_type: str = None
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
