
from .helpers.device import _WiserDevice
from .helpers.temp import _WiserTemperatureFunctions as tf
from .const import TEXT_UNKNOWN

class _WiserThresholdSensor(_WiserDevice):
    """Class representing a Wiser Room Stat device"""

    @property
    def device_id(self) -> int:
        """Get the current humidity reading of the room stat"""
        return self._device_type_data.get("DeviceId", None)

    @property
    def UUID(self) -> str:
        """Get the current humidity reading of the room stat"""
        return self._device_type_data.get("UUID", TEXT_UNKNOWN)

    @property
    def quantity(self) -> str:
        """Get the current humidity reading of the room stat"""
        return self._device_type_data.get("Quantity", TEXT_UNKNOWN)

    @property
    def current_value(self) -> float:
        """Get the current humidity reading of the room stat"""
        if self._device_type_data.get("Quantity")== "Temperature":
            return tf._from_wiser_temp(
            self._device_type_data.get("CurrentValue"), "current"
            )
        else:
            return self._device_type_data.get("CurrentValue", 0)

    @property
    def high_threshold(self) -> float:
        """Get the high threshold of the sensor setting"""
        return self._device_type_data.get("HighThreshold", 0)

    @property
    def medium_threshold(self) -> float:
        """Get the high threshold of the sensor setting"""
        return self._device_type_data.get("MediumThreshold", 0)

    @property
    def low_threshold(self) -> float:
        """Get the high threshold of the sensor setting"""
        return self._device_type_data.get("LowThreshold", 0)

    @property
    def interacts_with_room_climate(self) -> bool:
        """Get the current temperature measured by the room stat"""
        return self._device_type_data.get("InteractsWithRoomClimate", False)
        

class _WiserTemperatureHumiditySensor(_WiserThresholdSensor):
    """Class representing a Wiser TemperatureHumidity Sensor"""


class _WiserThresholdSensorCollection:
    """Class holding all wiser room stats"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserThresholdSensor]:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    # ThresholdSensors
    def get_by_id(self, threshold_sensor_id: int) -> _WiserThresholdSensor:
        """
        Gets a Threshold sensor object from the Threshold sensors id
        param id: id of threshold
        return: _Wiserthreshold_sensor object
        """

       
        try:
            return [threshold_sensor for threshold_sensor in self.all if threshold_sensor.id == threshold_sensor_id][
                0
            ]
        except IndexError:
            return None
        