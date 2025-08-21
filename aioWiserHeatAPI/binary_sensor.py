"""
Handles binary_sensor devices
"""

import inspect
from typing import Union
from .helpers.misc import is_value_in_list

from aioWiserHeatAPI import _LOGGER

from .helpers.battery import _WiserBattery
from .helpers.device import _WiserDevice
from .helpers.threshold import _WiserThresholdSensor

from .const import (
    TEXT_NONE,
    TEXT_ONEITHER,
    TEXT_UNKNOWN,
    WISERDEVICE,
    WiserWindowDoorEnableNotificationEnum,
    WiserWindowDoorTypeEnum,
    )
from .const import (WISERBINARYSENSOR)

class _WiserBinarySensor(_WiserDevice):
    """Class representing a Wiser Binary Sensor"""

    def __init__(self, *args):
        """Initialise."""
        super().__init__(*args)
        self._threshold_sensors: list[_WiserThresholdSensor] = []


    async def _send_command(self, cmd: dict, device_level: bool = False):
        """
        Send control command to the device
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        if device_level:
            result = await self._wiser_rest_controller._send_command(
                WISERDEVICE.format(self.id), cmd
            )
            if result:
                self._data = result
        else:
            result = await self._wiser_rest_controller._send_command(
                self._endpoint.format(self.device_type_id), cmd
            )
            if result:
                self._device_type_data = result
        if result:
            _LOGGER.debug(
                "Wiser bynarysensor - {} command successful".format(
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
    def sensorstatus(self) -> bool:
        """Get sensor status"""
        return self._device_type_data.get("SensorStatus")

    @property
    def interacts_with_room_climate(self) -> bool:
        """Get the if interacts with room climate"""
        return self._device_type_data.get("InteractsWithRoomClimate")

    async def set_interacts_with_room_climate(self, enabled: bool):
        if await self._send_command({"InteractsWithRoomClimate": str(enabled).lower()}):
            self._interacts_with_room_climate = enabled
            return True

    @property
    def available_type(self):
        """Get available enable notification"""
        return [action.value for action in WiserWindowDoorTypeEnum ]


    @property
    def type(self) -> str:
        """Get the type of device"""
        return self._device_type_data.get("Type")
    
    async def set_type(
    self, type: Union[WiserWindowDoorTypeEnum, str]
    ) -> bool:
        if isinstance(type, WiserWindowDoorTypeEnum):
            type = type.value
        if is_value_in_list(type, self.available_type):
            return await self._send_command({"Type": type})
        else:
            raise ValueError(
                f"{type} is not a valid type.  Valid types are {self.available_type}"
            )   

    @property
    def available_enable_notification(self):
        """Get available enable notification"""
        return [action.value for action in WiserWindowDoorEnableNotificationEnum ]

    @property
    def enable_notification(self) -> str:
        """Get if notifications is enable"""
        return self._device_type_data.get("EnableNotification")

    async def set_enable_notification(
    self, enable_notification: Union[WiserWindowDoorEnableNotificationEnum, str]
    ) -> bool:
        """Set  notifications enable for WindowDoor Sensor"""
        if isinstance(enable_notification, WiserWindowDoorEnableNotificationEnum):
            enable_notification = enable_notification.value
        if is_value_in_list(enable_notification, self.available_enable_notification):
            return await self._send_command({"EnableNotification": enable_notification})
        else:
            raise ValueError(
                f"{enable_notification} is not a valid mode.  Valid modes are {self.available_enable_notification}"
            )

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
