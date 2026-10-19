#added by LGO for Hub V2 new features LedIndicator for socket smart plug
import inspect
from typing import Union
from .helpers.misc import is_value_in_list
# end added by LGO for Hub V2 new features LedIndicator for socket smart plug

from .const import (
    TEXT_OFF, 
    TEXT_ON, 
    TEXT_UNKNOWN, 
    WiserDeviceModeEnum,
    WiserLightLedIndicatorEnum,
)
from .const import TEXT_OFF, TEXT_ON, TEXT_UNKNOWN, WiserDeviceModeEnum
from .helpers.device import _WiserElectricalDevice
from .helpers.equipment import _WiserEquipment

class _WiserSmartPlug(_WiserElectricalDevice):
    """Class representing a Wiser Smart Plug device"""

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

    # added by LGO
    # Hub V2  new features LedIndicatorfor socket smart plug
 
    @property
    def is_led_indicator_supported(self) -> bool:
        """Get is led indicator supported for the light"""

        return (
            True
            if self._device_type_data.get("IsLedIndicatorSupported", False)
            else False
        )

    @property
    def available_led_indicator(self):
        """Get available led indicator"""
        return [action.value for action in WiserLightLedIndicatorEnum]

    @property
    def led_indicator(self) -> str:
        """Get  led indicator for the light"""
        return self._device_type_data.get("LedIndicator", TEXT_UNKNOWN)

    async def set_led_indicator(
        self, led_indicator: Union[WiserLightLedIndicatorEnum, str]
    ) -> bool:
        if isinstance(led_indicator, WiserLightLedIndicatorEnum):
            led_indicator = led_indicator.value
        if is_value_in_list(led_indicator, self.available_led_indicator):
            return await self._send_command({"LedIndicator": led_indicator})
        else:
            raise ValueError(
                f"{led_indicator} is not a valid mode.  Valid modes are {self.available_led_indicator}"
            )
    # end added by LGO for Hub V2 new features LedIndicator for socket smart plug
    
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
