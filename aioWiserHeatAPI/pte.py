"""
Handles power tag energy devices
"""

from .const import TEXT_UNABLE, TEXT_UNKNOWN
from .helpers.device import _WiserDevice
from .helpers.equipment import _WiserEquipment


class _WiserPowerTagEnergy(_WiserDevice):
    """Class representing a Wiser Power Tag Energy device"""

    @property
    def delivered_power(self) -> int:
        """Get current power of device"""
        return self.equipment.power.current_summation_delivered

    @property
    def energy_export(self) -> str:
        """Get energy export status"""
        return self._device_type_data.get("EnergyExport", TEXT_UNABLE)

    @property
    def equipment(self) -> _WiserEquipment | None:
        """Get equipment data"""
        return (
            _WiserEquipment(self._device_type_data.get("EquipmentData"))
            if self._device_type_data.get("EquipmentData")
            else None
        )

    @property
    def grid_limit(self) -> int:
        """Get grid limit"""
        return self._device_type_data.get("GridLimit", 0)

    @property
    def grid_limit_uom(self) -> str:
        """Get grid limit uom"""
        return self._device_type_data.get("GridLimitUom", TEXT_UNKNOWN)

    @property
    def instantaneous_power(self) -> int:
        """Get current power of device"""
        return self.equipment.power.total_active_power

    @property
    def raw_total_active_power(self) -> int:
        """Get raw total active power of device"""
        return self._device_type_data.get("RawTotalActivePower", None)

    @property
    def received_power(self) -> int:
        """Get current power of device"""
        return self.equipment.power.current_summation_received

    @property
    def rfid(self) -> int:
        """Get rfid of device"""
        return self._data.get("RfId", 0)

    @property
    def self_consumption(self) -> bool:
        """Get self consumption"""
        return self._device_type_data.get("SelfConsumption", False)


class _WiserPowerTagEnergyCollection:
    """Class representing collection of Power Tag Energy devices"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserPowerTagEnergy]:
        """Return all power tags"""
        return list(self._items)

    @property
    def count(self) -> int:
        """Return number of power tags"""
        return len(self.all)

    def get_by_id(self, device_id: int) -> _WiserPowerTagEnergy:
        """
        Gets a Power Tag Energy object from the device id
        param id: id of power tag
        return: _WiserPowerTagEnergy object
        """
        try:
            return [
                power_tag
                for power_tag in self.all
                if power_tag.id == device_id
            ][0]
        except IndexError:
            return None

    def get_by_equipment_id(self, equipment_id: int) -> _WiserPowerTagEnergy:
        """
        Gets a Power Tag Energy object from the equipment id
        param id: id of power tag
        return: _WiserPowerTagEnergy object
        """
        try:
            return [
                power_tag
                for power_tag in self.all
                if power_tag.id == equipment_id
            ][0]
        except IndexError:
            return None
