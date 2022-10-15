from . import _LOGGER

from .helpers.device import _WiserDevice
from .helpers.temp import _WiserTemperatureFunctions as tf
from .helpers.battery import _WiserBattery


class _WiserSmartValve(_WiserDevice):
    """Class representing a Wiser Smart Valve device"""

    @property
    def battery(self):
        """Get battery information for smart valve"""
        return _WiserBattery(self._data)

    @property
    def current_target_temperature(self) -> float:
        """Get the smart valve current target temperature setting"""
        return tf._from_wiser_temp(self._device_type_data.get("SetPoint"))

    @property
    def current_temperature(self) -> float:
        """Get the current temperature measured by the smart valve"""
        return tf._from_wiser_temp(
            self._device_type_data.get("MeasuredTemperature"), "current"
        )

    @property
    def mounting_orientation(self) -> str:
        """Get the mouting orientation of the smart valve"""
        return self._device_type_data.get("MountingOrientation")

    @property
    def percentage_demand(self) -> int:
        """Get the current percentage demand of the smart valve"""
        return self._device_type_data.get("PercentageDemand")


class _WiserSmartValveCollection(object):
    """Class holding all wiser smart valves"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> dict:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, id: int) -> _WiserSmartValve:
        """
        Gets a SmartValve object from the SmartValves id
        param id: id of smart valve
        return: _WiserSmartValve object
        """
        try:
            return [smartvalve for smartvalve in self.all if smartvalve.id == id][0]
        except IndexError:
            return None
