from .const import TEMP_OFF, TEXT_UNKNOWN, WISERHEATINGACTUATOR, WiserTempLimitsEnum
from .helpers.device import _WiserDevice
from .helpers.equipment import _WiserEquipment
from .helpers.temp import _WiserTemperatureFunctions as tf
from .rest_controller import _WiserRestController


class _WiserTemperatureSensor:
    """Data structure for plug in temp sensor"""

    def __init__(self, data: dict, wiser_rest_controller: _WiserRestController, id):
        self._data = data
        self._id = id
        self._wiser_rest_controller = wiser_rest_controller

    def _send_command(self, cmd: dict):
        """
        Send control command to the temp sensor controller
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        return self._wiser_rest_controller._send_command(
            WISERHEATINGACTUATOR.format(self._id), cmd
        )

    @property
    def measured_temperature(self) -> float:
        """Get the temperature measured by the temperature sensor"""
        return tf._from_wiser_temp(
            self._data.get("MeasuredTemperature", None), "current"
        )

    @property
    def maximum_temperature(self) -> float:
        """Get the maximum temperature setting"""
        return tf._from_wiser_temp(
            self._data.get("MaximumTemperature", None), "floorHeatingMax"
        )

    async def set_maximum_temperature(self, temp: float):
        """Set the maximum temperature setting"""
        if temp >= WiserTempLimitsEnum.floorHeatingMax.value.get(
            "min"
        ) and temp <= WiserTempLimitsEnum.floorHeatingMax.value.get("max"):
            return await self._send_command(
                {
                    "FloorTemperatureSensor": {
                        "MaximumTemperature": tf._to_wiser_temp(temp, "floorHeatingMax")
                    }
                }
            )
        raise ValueError("Max temperature can only be between 5C and 40C")

    @property
    def minimum_temperature(self) -> float:
        """Get the minimum temperature setting"""
        return tf._from_wiser_temp(
            self._data.get("MinimumTemperature", None), "floorHeatingMin"
        )

    async def set_minimum_temperature(self, temp: float):
        """Set the minimum temperature setting"""
        if temp >= WiserTempLimitsEnum.floorHeatingMin.value.get(
            "min"
        ) and temp <= WiserTempLimitsEnum.floorHeatingMin.value.get("max"):
            return await self._send_command(
                {
                    "FloorTemperatureSensor": {
                        "MinimumTemperature": tf._to_wiser_temp(temp, "floorHeatingMin")
                    }
                }
            )
        raise ValueError("Max temperature can only be between 5C and 39C")

    @property
    def sensor_type(self) -> str:
        """Get the sensor type"""
        return self._data.get("SensorType", TEXT_UNKNOWN)

    @property
    def status(self) -> str:
        """Get the status"""
        return self._data.get("Status", TEXT_UNKNOWN)

    @property
    def temperature_offset(self) -> float:
        """Get the temperature offset"""
        return tf._from_wiser_temp(self._data.get("Offset", None), "floorHeatingOffset")

    async def set_temperature_offset(self, temp: float):
        """Set the temperature offset"""
        if temp >= WiserTempLimitsEnum.floorHeatingOffset.value.get(
            "min"
        ) and temp <= WiserTempLimitsEnum.floorHeatingOffset.value.get("max"):
            return await self._send_command(
                {
                    "FloorTemperatureSensor": {
                        "Offset": tf._to_wiser_temp(temp, "floorHeatingOffset")
                    }
                }
            )
        raise ValueError("Offset temperature can only be between -9C and 9C")


class _WiserHeatingActuator(_WiserDevice):
    """Class representing a Wiser Heating Actuator device"""

    @property
    def current_target_temperature(self) -> float:
        """Get the current target temperature setting"""
        return tf._from_wiser_temp(
            self._device_type_data.get("OccupiedHeatingSetPoint", TEMP_OFF)
        )

    @property
    def current_temperature(self) -> float:
        """Get the current measured temperature"""
        return tf._from_wiser_temp(
            self._device_type_data.get("MeasuredTemperature", TEMP_OFF), "current"
        )

    @property
    def delivered_power(self) -> int:
        """Get the amount of power delivered over time"""
        return self._device_type_data.get("CurrentSummationDelivered", 0)

    @property
    def equipment_id(self) -> int:
        """Get equipment id (v2 hub)"""
        return self._device_type_data.get("EquipmentId", 0)

    @property
    def equipment(self) -> str:
        """Get equipment data"""
        return (
            _WiserEquipment(self._device_type_data.get("EquipmentData"))
            if self._device_type_data.get("EquipmentData")
            else None
        )

    @property
    def floor_temperature_sensor(self) -> _WiserTemperatureSensor:
        """Get the temperature sensor object"""
        if self._device_type_data.get("FloorTemperatureSensor"):
            return _WiserTemperatureSensor(
                self._device_type_data.get("FloorTemperatureSensor", {}),
                self._wiser_rest_controller,
                self.id,
            )

    @property
    def instantaneous_power(self) -> int:
        """Get the amount of current passing through the device now"""
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
