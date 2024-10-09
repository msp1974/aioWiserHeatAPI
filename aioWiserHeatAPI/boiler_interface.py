from .helpers.device import _WiserDevice


class _WiserBoilerInterface(_WiserDevice):
    """Class representing a Wiser Boiler Interface"""

    @property
    def heating_channel_ids(self) -> list[int]:
        """Heating channel ids."""
        return self._device_type_data.get("HeatingChannelIds")


class _WiserBoilerInterfaceCollection:
    """Class holding all Wiser Boiler Interfaces"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserBoilerInterface]:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, id: int) -> _WiserBoilerInterface:
        """
        Gets a boiler interface object from the binary sensor id
        param id: id of boiler interface
        return: _WiserBoilerInterface object
        """
        try:
            return [
                boilerinterface
                for boilerinterface in self.all
                if boilerinterface.id == id
            ][0]
        except IndexError:
            return None
