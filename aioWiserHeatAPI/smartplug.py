from typing import Union

from .const import (
    TEXT_OFF,
    TEXT_ON,
    TEXT_UNKNOWN,
    WISERDEVICE,
    WiserDeviceModeEnum,
    WiserSmartPlugLedIndicatorEnum,
)
from .helpers.device import _WiserElectricalDevice
from .helpers.equipment import _WiserEquipment


class _WiserSmartPlug(_WiserElectricalDevice):
    """Class representing a Wiser Smart Plug device"""

    async def _send_command(self, cmd: dict, device_level: bool = False) -> bool:
        """Send commands using the ID belonging to the requested endpoint."""
        endpoint = (
            WISERDEVICE.format(self.id)
            if device_level
            else self._endpoint.format(self.device_type_id)
        )
        result = await self._wiser_rest_controller._send_command(endpoint, cmd)
        if not result:
            return False
        if device_level:
            self._data = result
        else:
            self._device_type_data = result
        return True

    @property
    def control_source(self) -> str:
        """Get the current control source of the smart plug"""
        return self._device_type_data.get("ControlSource", TEXT_UNKNOWN)

    @property
    def delivered_power(self) -> int:
        """Get the amount of current throught the plug over time"""
        return self._device_type_data.get("CurrentSummationDelivered", None)

    @property
    def equipment_id(self) -> int:
        """Get equipment id (v2 hub)"""
        return self._device_type_data.get("EquipmentId", 0)

    @property
    def equipment(self) -> _WiserEquipment | None:
        """Get equipment data"""
        return (
            _WiserEquipment(self._device_type_data.get("EquipmentData"))
            if self._device_type_data.get("EquipmentData")
            else None
        )

    @property
    def instantaneous_power(self) -> int:
        """Get the amount of current throught the plug now"""
        return self._device_type_data.get("InstantaneousDemand", None)

    @property
    def manual_state(self) -> str:
        """Get the current manual mode setting of the smart plug"""
        return self._device_type_data.get("ManualState", TEXT_UNKNOWN)

    @property
    def is_on(self) -> bool:
        """Get if the smart plug is on"""
        return True if self.output_state == TEXT_ON else False

    @property
    def output_state(self) -> str:
        """Get plug output state"""
        return self._device_type_data.get("OutputState", TEXT_OFF)

    @property
    def scheduled_state(self) -> str:
        """Get the current scheduled state of the smart plug"""
        return self._device_type_data.get("ScheduledState", TEXT_UNKNOWN)

    @property
    def is_led_indicator_supported(self) -> bool:
        """Return whether the smart plug supports LED indicator configuration."""
        return bool(self._device_type_data.get("IsLedIndicatorSupported", False))

    @property
    def available_led_indicator(self) -> list[str]:
        """Get available LED indicator modes."""
        return [mode.value for mode in WiserSmartPlugLedIndicatorEnum]

    @property
    def led_indicator(self) -> str:
        """Get the LED indicator mode for the smart plug."""
        return self._device_type_data.get("LedIndicator", TEXT_UNKNOWN)

    async def set_led_indicator(
        self, led_indicator: Union[WiserSmartPlugLedIndicatorEnum, str]
    ) -> bool:
        """Set the LED indicator using an enum or case-insensitive string."""
        if isinstance(led_indicator, WiserSmartPlugLedIndicatorEnum):
            led_indicator = led_indicator.value
        if isinstance(led_indicator, str):
            for mode in WiserSmartPlugLedIndicatorEnum:
                if led_indicator.casefold() == mode.value.casefold():
                    return await self._send_command({"LedIndicator": mode.value})
        raise ValueError(
            f"{led_indicator} is not a valid mode.  Valid modes are {self.available_led_indicator}"
        )

    @property
    def next_scheduled_date(self) -> str:
        """Get the next scheduled date for the smart plug"""
        return self._device_type_data.get("NextScheduledDate", TEXT_UNKNOWN)

    @property
    def next_scheduled_end_date(self) -> str:
        """Get the next scheduled end date for the smart plug"""
        return self._device_type_data.get("NextScheduledEndDate", TEXT_UNKNOWN)

    async def turn_on(self) -> bool:
        """
        Turn on the smart plug
        return: boolean
        """
        result = await self._send_command({"RequestOutput": TEXT_ON})
        if result:
            self._output_state = TEXT_ON
        return result

    async def turn_off(self) -> bool:
        """
        Turn off the smart plug
        return: boolean
        """
        result = await self._send_command({"RequestOutput": TEXT_OFF})
        if result:
            self._output_state = TEXT_OFF
        return result


class _WiserSmartPlugCollection(object):
    """Class holding all wiser smart plugs"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserSmartPlug]:
        return list(self._items)

    @property
    def available_modes(self) -> list[str]:
        return [mode.value for mode in WiserDeviceModeEnum]

    @property
    def count(self) -> int:
        return len(self.all)

    # Smartplugs
    def get_by_id(self, smartplug_id: int) -> _WiserSmartPlug:
        """
        Gets a SmartPlug object from the SmartPlugs id
        param id: id of smart plug
        return: _WiserSmartPlug object
        """
        try:
            return [
                smartplug
                for smartplug in self.all
                if smartplug.id == smartplug_id
            ][0]
        except IndexError:
            return None
