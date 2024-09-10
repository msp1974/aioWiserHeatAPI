"""
Handles binary_sensor devices
"""

from .helpers.device import _WiserDevice

class _WiserBinarySensor(_WiserDevice):
    """Class representing a Wiser Binary Sensor"""

class _WiserBinarySensor1(_WiserDevice):
    """Class representing a Wiser Binary Sensor"""

    @property
    def active(self) -> bool:
        """Get if is active"""
        return self._device_type_data.get("Active")

    @property
    def interacts_with_room_climate(self) -> bool:
        """Get the if interacts with room climate"""
        return self._device_type_data.get("InteractsWithRoomClimate")

    @property
    def type(self) -> str:
        """Get the type of device"""
        return self._device_type_data.get("Type")

    @property
    def enable_notification(self) -> str:
        """Get if notifications is enable"""
        return self._device_type_data.get("EnableNotification")


class _WiserBinarySensorCollection(object):
    """Class holding all Wiser Binary Sensors"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> dict:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, id: int) -> _WiserBinarySensor:
        """
        Gets a binarysensor object from the binary sensor id
        param id: id of binary sensor
        return: _WiserBinarySensor object
        """
        try:
            return [
                binarysensor for binarysensor in self.all if binarysensor.id == id
            ][0]
        except IndexError:
            return None