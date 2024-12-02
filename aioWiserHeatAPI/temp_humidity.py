from aioWiserHeatAPI.helpers.threshold import _WiserThresholdSensor

from .helpers.battery import _WiserBattery
from .helpers.device import _WiserDevice


class _WiserTempHumidity(_WiserDevice):
    """Class representing a Temp Humidity device"""

    def __init__(self, *args):
        """Initialise."""
        super().__init__(*args)
        self._threshold_sensors: list[_WiserThresholdSensor] = []

    @property
    def battery(self) -> _WiserBattery:
        """Get the battery information for the device"""
        return _WiserBattery(self._data)

    @property
    def threshold_sensors(self) -> list[_WiserThresholdSensor]:
        """Get threshold sensors."""
        return self._threshold_sensors


class _WiserTempHumidityCollection:
    """Class holding all wiser temp humidity sensors"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserTempHumidity]:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    # Roomstats
    def get_by_id(self, temphum_id: int) -> _WiserTempHumidity:
        """
        Gets a temp humidity object from the device id
        param id: id of device
        return: _WiserTempHumidity object
        """
        for temphum in self.all:
            if temphum.id == temphum_id:
                return temphum
        return None
