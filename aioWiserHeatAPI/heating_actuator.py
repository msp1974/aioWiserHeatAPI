from . import _LOGGER

from .const import TEMP_OFF, TEXT_UNKNOWN, WISERHEATINGACTUATOR, WISERDEVICE
from .helpers.device import _WiserDevice
from .helpers.temp import _WiserTemperatureFunctions as tf


class _WiserHeatingActuator(_WiserDevice):
    """Class representing a Wiser Heating Actuator device"""

    @property
    def current_target_temperature(self) -> float:
        """Get the smart valve current target temperature setting"""
        return tf._from_wiser_temp(
            self._device_type_data.get("OccupiedHeatingSetPoint", TEMP_OFF)
        )

    @property
    def current_temperature(self) -> float:
        """Get the current temperature measured by the smart valve"""
        return tf._from_wiser_temp(
            self._device_type_data.get("MeasuredTemperature", TEMP_OFF), "current"
        )

    @property
    def delivered_power(self) -> int:
        """Get the amount of current throught the plug over time"""
        return self._device_type_data.get("CurrentSummationDelivered", 0)

    @property
    def instantaneous_power(self) -> int:
        """Get the amount of current throught the plug now"""
        return self._device_type_data.get("InstantaneousDemand", 0)

    @property
    def output_type(self) -> str:
        """Get output type"""
        return self._device_type_data.get("OutputType", TEXT_UNKNOWN)


class _WiserHeatingActuatorCollection(object):
    """Class holding all wiser heating actuators"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> dict:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, id: int) -> _WiserHeatingActuator:
        """
        Gets a Heating Actuator object from the Heating Actuators id
        param id: id of smart valve
        return: _WiserSmartValve object
        """
        try:
            return [
                heating_actuator
                for heating_actuator in self.all
                if heating_actuator.id == id
            ][0]
        except IndexError:
            return None
