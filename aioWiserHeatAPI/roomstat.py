from . import _LOGGER

from .helpers.device import _WiserDevice
from .helpers.battery import _WiserBattery
from .helpers.temp import _WiserTemperatureFunctions as tf


class _WiserRoomStat(_WiserDevice):
    """Class representing a Wiser Room Stat device"""

    @property
    def battery(self) -> _WiserBattery:
        """Get the battery information for the room stat"""
        return _WiserBattery(self._data)

    @property
    def current_humidity(self) -> int:
        """Get the current humidity reading of the room stat"""
        return self._device_type_data.get("MeasuredHumidity", 0)

    @property
    def current_target_temperature(self) -> float:
        """Get the room stat current target temperature setting"""
        return tf._from_wiser_temp(self._device_type_data.get("SetPoint", 0))

    @property
    def current_temperature(self) -> float:
        """Get the current temperature measured by the room stat"""
        return tf._from_wiser_temp(
            self._device_type_data.get("MeasuredTemperature", 0), "current"
        )


class _WiserRoomStatCollection(object):
    """Class holding all wiser room stats"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    # Roomstats
    def get_by_id(self, id: int) -> _WiserRoomStat:
        """
        Gets a RoomStat object from the RoomStats id
        param id: id of room stat
        return: _WiserRoomStat object
        """
        for roomstat in self.all:
            if roomstat.id == id:
                return roomstat
        return None
