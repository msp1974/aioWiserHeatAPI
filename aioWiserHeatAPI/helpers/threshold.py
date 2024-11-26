import inspect

from .. import _LOGGER
from ..const import TEXT_UNKNOWN
from ..rest_controller import _WiserRestController
from .temp import _WiserTemperatureFunctions as tf


class _WiserThresholdSensor:
    """Class representing a Wiser threshold sensor for a WIser device."""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        endpoint: str,
        data: dict,
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._endpoint = endpoint
        self._data = data

    async def _send_command(self, cmd: dict):
        """
        Send control command to the Threshold sensor
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        result = await self._wiser_rest_controller._send_command(
            self._endpoint.format(self.id), cmd
        )
        if result:
            self._device_type_data = result
        if result:
            _LOGGER.debug(
                "Wiser light - {} command successful".format(
                    inspect.stack()[1].function
                )
            )
            return True
        return False

    @property
    def id(self) -> str:
        """Get the current humidity reading of the room stat"""
        return self._data.get("id", 0)

    @property
    def UUID(self) -> str:
        """Get the current humidity reading of the room stat"""
        return self._data.get("UUID", TEXT_UNKNOWN)

    @property
    def quantity(self) -> str:
        """Get the current humidity reading of the room stat"""
        return self._data.get("Quantity", TEXT_UNKNOWN)

    @property
    def current_value(self) -> float:
        """Get the current humidity reading of the room stat"""
        if self._data.get("Quantity") == "Temperature":
            return tf._from_wiser_temp(self._data.get("CurrentValue"), "current")
        else:
            return self._data.get("CurrentValue", 0)

    @property
    def high_threshold(self) -> float:
        """Get the high threshold of the sensor setting"""
        return self._data.get("HighThreshold", 0)

    @property
    def medium_threshold(self) -> float:
        """Get the high threshold of the sensor setting"""
        return self._data.get("MediumThreshold", 0)

    @property
    def low_threshold(self) -> float:
        """Get the high threshold of the sensor setting"""
        return self._data.get("LowThreshold", 0)

    @property
    def current_level(self) -> str:
        """Get the high threshold of the sensor setting"""
        return self._data.get("CurrentLevel", TEXT_UNKNOWN)

    @property
    def interacts_with_room_climate(self) -> bool:
        """Get the current temperature measured by the room stat"""
        return self._data.get("InteractsWithRoomClimate", False)

    async def set_interacts_with_room_climate(self, enabled: bool):
        if await self._send_command({"InteractsWithRoomClimate": str(enabled).lower()}):
            self._interacts_with_room_climate = enabled
            return True
