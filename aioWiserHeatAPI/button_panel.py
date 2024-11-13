from typing import Any

from .helpers.device import _WiserDevice


class _WiserButtonPanel(_WiserDevice):
    """Class representing a Wiser Button Panel"""

    @property
    def number_of_gangs(self) -> list[int]:
        """Number of gangs."""
        return self._device_type_data.get("NumberOfGangs")

    @property
    def events(self) -> list[dict[str, Any]]:
        """Events info."""
        return self._device_type_data.get("Events")


class _WiserButtonPanelCollection:
    """Class holding all Wiser Button Panels"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserButtonPanel]:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, id: int) -> _WiserButtonPanel:
        """
        Gets a button panel object from the sensor id
        param id: id of button panel
        return: _WiserButtonPanel object
        """
        try:
            return [buttonpanel for buttonpanel in self.all if buttonpanel.id == id][0]
        except IndexError:
            return None
