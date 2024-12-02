"""
Handles power tag energy devices
"""

import inspect

from aioWiserHeatAPI import _LOGGER

from .const import TEXT_OFF, TEXT_ON, TEXT_UNABLE, TEXT_UNKNOWN, WISERDEVICE
from .helpers.device import _WiserElectricalDevice
from .helpers.equipment import _WiserEquipment


class _WiserPowerTagControl(_WiserElectricalDevice):
    """Class representing a Wiser Power Tag Energy device"""

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
    def control_source(self) -> str:
        """Get the current control source."""
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
    def target_state(self) -> str:
        """Get the target state."""
        return self._device_type_data.get("TargetState", TEXT_UNKNOWN)

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
    def actuator_type(self) -> str:
        """Get actuator type."""
        return self._device_type_data.get("ActuatorType", TEXT_UNKNOWN)

    @property
    def feedback_type(self) -> str:
        """Get feedback type."""
        return self._device_type_data.get("FeedbackType", TEXT_UNKNOWN)

    @property
    def polarity(self) -> str:
        """Get polarity."""
        return self._device_type_data.get("Polarity", TEXT_UNKNOWN)

    @property
    def relay_action(self) -> str:
        """Get relay action."""
        return self._device_type_data.get("RelayAction", TEXT_UNKNOWN)

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

    @property
    def energy_export(self) -> str:
        """Get energy export status"""
        return self._device_type_data.get("EnergyExport", TEXT_UNABLE)

    @property
    def rfid(self) -> int:
        """Get rfid of device"""
        return self._data.get("RfId", 0)

    @property
    def self_consumption(self) -> bool:
        """Get self consumption"""
        return self._device_type_data.get("SelfConsumption", False)


class _WiserPowerTagControlCollection:
    """Class representing collection of Power Tag Energy devices"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserPowerTagControl]:
        """Return all power tags"""
        return list(self._items)

    @property
    def count(self) -> int:
        """Return number of power tags"""
        return len(self.all)

    def get_by_id(self, device_id: int) -> _WiserPowerTagControl:
        """
        Gets a Power Tag Energy object from the device id
        param id: id of power tag
        return: _WiserPowerTagEnergy object
        """
        try:
            return [power_tag for power_tag in self.all if power_tag.id == device_id][0]
        except IndexError:
            return None

    def get_by_equipment_id(self, equipment_id: int) -> _WiserPowerTagControl:
        """
        Gets a Power Tag Energy object from the equipment id
        param id: id of power tag
        return: _WiserPowerTagEnergy object
        """
        try:
            return [
                power_tag for power_tag in self.all if power_tag.id == equipment_id
            ][0]
        except IndexError:
            return None
