import inspect
from . import _LOGGER

from .const import TEXT_ON, TEXT_OFF, TEXT_UNKNOWN, WISERDEVICE, WiserDeviceModeEnum
from .helpers.device import _WiserElectricalDevice


class _WiserOutputRange(object):
    """Data structure for min/max output range"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def minimum(self) -> int:
        """Get min value"""
        if self._data:
            return self._data.get("Minimum")
        return None

    @property
    def maximum(self) -> int:
        """Get max value"""
        if self._data:
            return self._data.get("Maximum")
        return None


class _WiserLight(_WiserElectricalDevice):
    """Class representing a Wiser Light device"""

    async def _send_command(self, cmd: dict, device_level: bool = False):
        """
        Send control command to the smart plug
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
                self._endpoint.format(self.light_id), cmd
            )
            if result:
                self._device_type_data = result
        if result:
            _LOGGER.debug(
                "Wiser smart plug - {} command successful".format(
                    inspect.stack()[1].function
                )
            )
            return True
        return False

    @property
    def control_source(self) -> str:
        """Get the current control source of the light"""
        return self._device_type_data.get("ControlSource", TEXT_UNKNOWN)

    @property
    def current_state(self) -> str:
        """Get if light is on"""
        return self._device_type_data.get("CurrentState", 0)

    @property
    def is_dimmable(self) -> bool:
        """Get if the light is dimmable"""
        return True if self._device_type_data.get("IsDimmable", False) else False

    @property
    def is_on(self) -> bool:
        """Get if the light is on"""
        return True if self.current_state == TEXT_ON else False

    @property
    def light_id(self) -> int:
        """Get id of shutter"""
        return self._device_type_data.get("id", 0)

    @property
    def target_state(self) -> int:
        """Get target state of light"""
        return self._device_type_data.get("TargetState", 0)

    async def turn_on(self) -> bool:
        """
        Turn on the light at current brightness level
        return: boolean
        """
        return await self._send_command({"RequestOverride": {"State": TEXT_ON}})

    async def turn_off(self) -> bool:
        """
        Turn off the light
        return: boolean
        """
        return await self._send_command({"RequestOverride": {"State": TEXT_OFF}})


class _WiserDimmableLight(_WiserLight):
    """Class representing a Wiser Dimmable Light device"""

    @property
    def current_level(self) -> int:
        """Get amount light is on"""
        return self._device_type_data.get("CurrentLevel", 0)

    @property
    def current_percentage(self) -> int:
        """Get percentage amount light is on"""
        return self._device_type_data.get("CurrentPercentage", 0)

    async def set_current_percentage(self, percentage: int):
        """Set current brightness percentage"""
        if percentage >= 0 and percentage <= 100:
            return await self._send_command(
                {"RequestOverride": {"State": TEXT_ON, "Percentage": percentage}}
            )
        else:
            raise ValueError(f"Brightness level percentage must be between 0 and 100")

    @property
    def manual_level(self) -> int:
        """Get manual level of light"""
        return self._device_type_data.get("ManualLevel", 0)

    @property
    def override_level(self) -> int:
        """Get override level of light"""
        return self._device_type_data.get("OverrideLevel", 0)

    @property
    def output_range(self) -> _WiserOutputRange:
        """Get output range min/max."""
        # TODO: Add setter for min max values
        return _WiserOutputRange(self._device_type_data.get("OutputRange", None))

    @property
    def scheduled_percentage(self) -> int:
        """Get the scheduled percentage for the light"""
        return self._data.get("ScheduledPercentage", 0)

    @property
    def target_percentage(self) -> int:
        """Get target percentage brightness of light"""
        return self._device_type_data.get("TargetPercentage", 0)


class _WiserLightCollection(object):
    """Class holding all wiser lights"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list:
        return list(self._items)

    @property
    def available_modes(self):
        return [mode.value for mode in WiserDeviceModeEnum]

    @property
    def count(self) -> int:
        return len(self.all)

    @property
    def dimmable_lights(self) -> list:
        return list(
            dimmable_lights
            for dimmable_lights in self.all
            if dimmable_lights.is_dimmable
        )

    @property
    def onoff_lights(self) -> list:
        return list(
            onoff_lights for onoff_lights in self.all if not onoff_lights.is_dimmable
        )

    def get_by_id(self, id: int) -> _WiserLight:
        """
        Gets a Light object from the Lights device id
        param id: device id of shutter
        return: _WiserShutter object
        """
        try:
            return [light for light in self.all if light.id == id][0]
        except IndexError:
            return None

    def get_by_light_id(self, light_id: int) -> _WiserLight:
        """
        Gets a Light object from the Lights id
        param id: id of light
        return: _WiserLight object
        """
        try:
            return [light for light in self.all if light.light_id == light_id][0]
        except IndexError:
            return None

    def get_by_room_id(self, room_id: int) -> list:
        """
        Gets a Light object from the Lights room_id
        param id: room_id of light
        return: list of _WiserLight objects
        """
        return [light for light in self.all if light.room_id == room_id]
