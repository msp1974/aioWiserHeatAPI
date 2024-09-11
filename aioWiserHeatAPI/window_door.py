"""
Handles WindowDoor devices
"""

from .helpers.device import _WiserDevice


class _WiserWindowDoor(_WiserDevice):
    """Class representing a Wiser WindowDoor Sensor"""

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


class _WiserWindowDoorCollection(object):
    """Class holding all Wiser Binary Sensors"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> dict:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, id: int) -> _WiserWindowDoor:
        """
        Gets a binarysensor object from the binary sensor id
        param id: id of binary sensor
        return: _WiserBinarySensor object
        """
        try:
            return [
                windowdoor for windowdoor in self.all if windowdoor.id == id
            ][0]
        except IndexError:
            return None