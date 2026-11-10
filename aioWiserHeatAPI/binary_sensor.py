"""
Handles binary_sensor devices
"""

import inspect

from aioWiserHeatAPI import _LOGGER

from .const import WiserWindowDoorEnableNotificationEnum
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
    def enable_notification(self) -> str | None:
        """Return the native notification mode, when supported."""
        return self._device_type_data.get("EnableNotification")

    @property
    def available_enable_notification(self) -> list[str]:
        """Return the native notification modes accepted by the hub."""
        return [mode.value for mode in WiserWindowDoorEnableNotificationEnum]

    @property
    def notification_enabled(self) -> bool | None:
        """Return whether any native notification mode is enabled."""
        mode = self.enable_notification
        if mode is None:
            return None
        if isinstance(mode, bool):
            return mode
        return mode != WiserWindowDoorEnableNotificationEnum.none.value

    async def set_enable_notification(
        self,
        enable_notification: WiserWindowDoorEnableNotificationEnum | str,
    ) -> bool:
        """Set the native notification mode for this sensor."""
        if isinstance(
            enable_notification, WiserWindowDoorEnableNotificationEnum
        ):
            enable_notification = enable_notification.value
        if enable_notification not in self.available_enable_notification:
            raise ValueError(
                f"{enable_notification} is not a valid notification mode. "
                f"Valid modes are {self.available_enable_notification}"
            )
        await self._wiser_rest_controller._send_command(
            self._endpoint.format(self.device_type_id),
            {"EnableNotification": enable_notification},
        )
        self._device_type_data["EnableNotification"] = enable_notification
        return True

    async def set_notification_enabled(self, enabled: bool) -> bool:
        """Enable or disable native notifications for this sensor."""
        return await self.set_enable_notification(
            WiserWindowDoorEnableNotificationEnum.oneither
            if enabled
            else WiserWindowDoorEnableNotificationEnum.none
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
