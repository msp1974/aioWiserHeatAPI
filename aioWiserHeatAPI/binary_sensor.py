"""
Handles binary_sensor devices
"""

import inspect
from typing import Union
from .helpers.misc import is_value_in_list

from .helpers.battery import _WiserBattery
from .helpers.device import _WiserDevice

from .const import (
    TEXT_NONE,
    TEXT_ONEITHER,
    TEXT_UNKNOWN,
    WISERDEVICE,
    WiserWindowDoorEnableNotificationEnum,
    )

class _WiserBinarySensor(_WiserDevice):
    """Class representing a Wiser Binary Sensor"""

    @property
    def active(self) -> bool:
        """Get if is active"""
        return self._device_type_data.get("Active")

    @property
    def type(self) -> str:
        """Get the type of device"""
        return self._device_type_data.get("Type")


    @property
    def interacts_with_room_climate(self) -> bool:
        """Get the if interacts with room climate"""
        return self._device_type_data.get("InteractsWithRoomClimate")


    async def set_interacts_with_room_climate(self, enabled: bool):
        if await self._send_command({"InteractsWithRoomClimate": str(enabled).lower()}):
            self._interacts_with_room_climate = enabled
            return True

    @property
    def binary_sensor_id(self) -> int:
        """Get id of binary sensor"""
        return self._device_type_data.get("id", 0)

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
