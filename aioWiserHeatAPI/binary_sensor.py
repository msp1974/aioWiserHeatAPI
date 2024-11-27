"""
Handles binary_sensor devices
"""

import inspect

from aioWiserHeatAPI import _LOGGER

from .helpers.battery import _WiserBattery
from .helpers.device import _WiserDevice
from .helpers.threshold import _WiserThresholdSensor


class _WiserBinarySensor(_WiserDevice):
    """Class representing a Wiser Binary Sensor"""

    def __init__(self, *args):
        """Initialise."""
        super().__init__(*args)
        self._threshold_sensors: list[_WiserThresholdSensor] = []

    async def _send_command(self, cmd: dict):
        """
        Send control command to the Threshold sensor
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        result = await self._wiser_rest_controller._send_command(
            self._endpoint.format(self.device_type_id), cmd
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
    def active(self) -> bool:
        """Get if is active"""
        return self._device_type_data.get("Active")

    @property
    def interacts_with_room_climate(self) -> bool:
        """Get the if interacts with room climate"""
        return self._device_type_data.get("InteractsWithRoomClimate")

    async def set_interacts_with_room_climate(self, enabled: bool):
        if await self._send_command({"InteractsWithRoomClimate": str(enabled).lower()}):
            self._interacts_with_room_climate = enabled
            return True

    @property
    def type(self) -> str:
        """Get the type of device"""
        return self._device_type_data.get("Type")

    @property
    def enable_notification(self) -> str:
        """Get if notifications is enable"""
        return self._device_type_data.get("EnableNotification")

    @property
    def battery(self) -> _WiserBattery:
        """Get the battery information for the smokealarm"""
        return _WiserBattery(self._data)

    @property
    def threshold_sensors(self) -> list[_WiserThresholdSensor]:
        """Get threshold sensors."""
        return self._threshold_sensors


class _WiserWindowDoorSensor(_WiserBinarySensor):
    """Class representing a Wiser WindowDoor Sensor"""


class _WiserBinarySensorCollection:
    """Class holding all Wiser Binary Sensors"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserBinarySensor]:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, id: int) -> _WiserBinarySensor:
        """
        Gets a binarysensor object from the binary sensor id
        param id: id of binary sensor
        return: _WiserBinarySensor object
        """
        try:
            return [binarysensor for binarysensor in self.all if binarysensor.id == id][
                0
            ]
        except IndexError:
            return None
