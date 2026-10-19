from .helpers.battery import _WiserBattery
from .helpers.device import _WiserDevice
from .helpers.temp import _WiserTemperatureFunctions as tf
from .const import TEXT_UNKNOWN

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

# added by LGO for compatibility with Wiser Heat 202510
    @property
    def window_state(self) -> str:
        """Get the window state"""
        if self._device_type_data.get("WindowState") == "Closed":
            return False
        elif self._device_type_data.get("WindowState") in ["Open","Opened"]:
            return True 
        else:    
            return TEXT_UNKNOWN
    
    @property
    def external_roomstat_temperature(self) -> int:
        """Get the external roomstat temperature"""
        return tf._from_wiser_temp(
            self._device_type_data.get("ExternalRoomStatTemperature"), "current"
        )

    @property
    def room_id(self) -> int:
        """Get the room_id of the smart valve"""
        return self._device_type_data.get("RoomId",None)


# end added by LGO for compatibility with Wiser Heat 202510


class _WiserSmartValveCollection(object):
    """Class holding all wiser smart valves"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserSmartValve]:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, smartvalve_id: int) -> _WiserSmartValve:
        """
        Gets a SmartValve object from the SmartValves id
        param id: id of smart valve
        return: _WiserSmartValve object
        """
        try:
            return [
                smartvalve
                for smartvalve in self.all
                if smartvalve.id == smartvalve_id
            ][0]
        except IndexError:
            return None
