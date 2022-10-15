from . import _LOGGER

from .helpers.device import _WiserElectricalDevice

from .const import TEXT_UNKNOWN, TEXT_OFF, TEXT_ON, WiserDeviceModeEnum

import inspect


class _WiserSmartPlug(_WiserElectricalDevice):
    """Class representing a Wiser Smart Plug device"""

    @property
    def control_source(self) -> str:
        """Get the current control source of the smart plug"""
        return self._device_type_data.get("ControlSource", TEXT_UNKNOWN)

    @property
    def delivered_power(self) -> int:
        """Get the amount of current throught the plug over time"""
        return self._device_type_data.get("CurrentSummationDelivered", -1)

    @property
    def instantaneous_power(self) -> int:
        """Get the amount of current throught the plug now"""
        return self._device_type_data.get("InstantaneousDemand", -1)

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
    def all(self) -> dict:
        return list(self._items)

    @property
    def available_modes(self) -> list:
        return [mode.value for mode in WiserDeviceModeEnum]

    @property
    def count(self) -> int:
        return len(self.all)

    # Smartplugs
    def get_by_id(self, id: int) -> _WiserSmartPlug:
        """
        Gets a SmartPlug object from the SmartPlugs id
        param id: id of smart plug
        return: _WiserSmartPlug object
        """
        try:
            return [smartplug for smartplug in self.all if smartplug.id == id][0]
        except IndexError:
            return None
