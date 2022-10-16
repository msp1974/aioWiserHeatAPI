from . import _LOGGER
from .const import (
    TEXT_UNKNOWN,
    WISERHEATINGACTUATOR,
    WISERLIGHT,
    WISERROOMSTAT,
    WISERSHUTTER,
    WISERSMARTPLUG,
    WISERSMARTVALVE,
    WISERUFHCONTROLLER,
)
import enum

from .rest_controller import _WiserRestController
from .roomstat import _WiserRoomStat, _WiserRoomStatCollection
from .schedule import _WiserScheduleCollection, WiserScheduleTypeEnum
from .smartplug import _WiserSmartPlug, _WiserSmartPlugCollection
from .smartvalve import _WiserSmartValve, _WiserSmartValveCollection
from .heating_actuator import _WiserHeatingActuator, _WiserHeatingActuatorCollection
from .shutter import _WiserShutter, _WiserShutterCollection
from .ufh import _WiserUFHController, _WiserUFHControllerCollection
from .light import _WiserLight, _WiserDimmableLight, _WiserLightCollection


class _WiserDeviceTypeEnum(enum.Enum):
    iTRV = "SmartValve"
    RoomStat = "RoomStat"
    SmartPlug = "SmartPlug"
    HeatingActuator = "HeatingActuator"
    UnderFloorHeating = "UnderFloorHeating"
    Shutter = "Shutter"
    OnOffLight = "Light"
    DimmableLight = "Light"


PRODUCT_TYPE_CONFIG = {
    "iTRV": {
        "class": _WiserSmartValve,
        "collection": _WiserSmartValveCollection,
        "endpoint": WISERSMARTVALVE,
        "heating": True,
    },
    "RoomStat": {
        "class": _WiserRoomStat,
        "collection": _WiserRoomStatCollection,
        "endpoint": WISERROOMSTAT,
        "heating": True,
    },
    "HeatingActuator": {
        "class": _WiserHeatingActuator,
        "collection": _WiserHeatingActuatorCollection,
        "endpoint": WISERHEATINGACTUATOR,
        "heating": True,
    },
    "UnderFloorHeating": {
        "class": _WiserUFHController,
        "collection": _WiserUFHControllerCollection,
        "endpoint": WISERUFHCONTROLLER,
        "heating": True,
    },
    "SmartPlug": {
        "class": _WiserSmartPlug,
        "collection": _WiserSmartPlugCollection,
        "endpoint": WISERSMARTPLUG,
        "schedule_type": WiserScheduleTypeEnum.onoff,
    },
    "Shutter": {
        "class": _WiserShutter,
        "collection": _WiserShutterCollection,
        "endpoint": WISERSHUTTER,
        "device_id_field": "DeviceId",
        "schedule_type": WiserScheduleTypeEnum.level,
    },
    "OnOffLight": {
        "class": _WiserLight,
        "collection": _WiserLightCollection,
        "endpoint": WISERLIGHT,
        "device_id_field": "DeviceId",
        "schedule_type": WiserScheduleTypeEnum.level,
    },
    "DimmableLight": {
        "class": _WiserDimmableLight,
        "collection": _WiserLightCollection,
        "endpoint": WISERLIGHT,
        "device_id_field": "DeviceId",
        "schedule_type": WiserScheduleTypeEnum.level,
    },
}


class _WiserDeviceCollection(object):
    """Class holding all wiser devices"""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        domain_data: dict,
        schedules: _WiserScheduleCollection,
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._device_data = domain_data.get("Device", {})
        self._domain_data = domain_data
        self._schedules = schedules
        self._device_collection = {}

        self._build()

    def _build(self):
        """Build collection of devices by type"""

        # Instantiate collection classes
        for device_type in _WiserDeviceTypeEnum:
            if (
                device_type.value not in self._device_collection
                and device_type.name in PRODUCT_TYPE_CONFIG
            ):
                self._device_collection[device_type.value] = PRODUCT_TYPE_CONFIG[
                    device_type.name
                ].get("collection")()

        # Iterate device data for all known device types
        if self._device_data:
            for device in self._device_data:
                device_type = device.get("ProductType", TEXT_UNKNOWN)
                if device_type in PRODUCT_TYPE_CONFIG:
                    device_config = PRODUCT_TYPE_CONFIG[device_type]

                    device_info = [
                        device_info
                        for device_info in self._domain_data.get(
                            _WiserDeviceTypeEnum[device_type].value
                        )
                        if device_info.get(device_config.get("device_id_field", "id"))
                        == device.get("id")
                    ]

                    # Get class to create and collection to append for device
                    device_class = PRODUCT_TYPE_CONFIG[device_type].get("class")

                    # If heating device add room id
                    if device_config.get("heating"):
                        device_info[0]["RoomId"] = self._get_temp_device_room_id(
                            self._domain_data, device.get("id")
                        )

                    # If schedule device add schedule
                    if device_config.get("schedule_type"):
                        device_schedule = [
                            schedule
                            for schedule in self._schedules.get_by_type(
                                device_config.get("schedule_type")
                            )
                            if schedule.id == device_info[0].get("ScheduleId")
                        ]
                    else:
                        device_schedule = None

                    # Add device to collection
                    self._device_collection[
                        _WiserDeviceTypeEnum[device_type].value
                    ]._items.append(
                        device_class(
                            self._wiser_rest_controller,
                            device_config.get("endpoint"),
                            device,
                            device_info[0],
                            device_schedule[0] if device_schedule else None,
                        )
                    )

    def _get_temp_device_room_id(self, domain_data: dict, device_id: int) -> int:
        rooms = domain_data.get("Room")
        for room in rooms:
            room_device_list = []
            room_device_list.extend(room.get("SmartValveIds", []))
            room_device_list.extend(room.get("HeatingActuatorIds", []))
            room_device_list.append(room.get("RoomStatId"))
            room_device_list.append(room.get("UnderFloorHeatingId"))
            if device_id in room_device_list:
                return room.get("id")
        return 0

    @property
    def all(self):
        items = []
        for key in self._device_collection:
            items.extend(self._device_collection[key].all)
        return items

    @property
    def count(self) -> int:
        return len(self.all)

    @property
    def heating_actuators(self):
        return self._device_collection["HeatingActuator"]

    @property
    def lights(self):
        return self._device_collection["Light"]

    @property
    def roomstats(self):
        return self._device_collection["RoomStat"]

    @property
    def shutters(self):
        return self._device_collection["Shutter"]

    @property
    def smartplugs(self):
        return self._device_collection["SmartPlug"]

    @property
    def smartvalves(self):
        return self._device_collection["SmartValve"]

    @property
    def ufh_controllers(self):
        return self._device_collection["UnderFloorHeating"]

    def get_by_id(self, id: int):
        """
        Gets a device object from the devices id
        param id: id of device
        return: Any of _WiserSmartValve, _WiserRoomStat, _WiserHeatingActuator, _WiserUFHController, _WiserSmartPlug, _WiserLight, _WiserDimmableLight, _WiserShutter objects
        """
        try:
            return [device for device in self.all if device.id == id][0]
        except IndexError:
            return None

    def get_by_room_id(self, room_id: int) -> list:
        """
        Gets a list of devices belonging to the room id
        param room_id: the id of the room
        return: Any of _WiserSmartValve, _WiserRoomStat, _WiserHeatingActuator, _WiserUFHController, _WiserSmartPlug, _WiserLight, _WiserDimmableLight, _WiserShutter objects
        """
        try:
            return [device for device in self.all if device.room_id == room_id]
        except IndexError:
            return None

    def get_by_node_id(self, node_id: int):
        """
        Gets a device object from the devices zigbee node id
        param node_id: zigbee node id of device
        return: Any of _WiserSmartValve, _WiserRoomStat, _WiserHeatingActuator, _WiserUFHController, _WiserSmartPlug, _WiserLight, _WiserDimmableLight, _WiserShutter objects
        """
        try:
            return [device for device in self.all if device.node_id == node_id][0]
        except IndexError:
            return None

    def get_by_serial_number(self, serial_number: str):
        """
        Gets a device object from the devices serial number
        param node_id: serial number of device
        return: Any of _WiserSmartValve, _WiserRoomStat, _WiserHeatingActuator, _WiserUFHController, _WiserSmartPlug, _WiserLight, _WiserDimmableLight, _WiserShutter objects
        """
        try:
            return [
                device for device in self.all if device.serial_number == serial_number
            ][0]
        except IndexError:
            return None

    def get_by_parent_node_id(self, node_id: int) -> list:
        """
        Gets a list of device from the devices zigbee parent node id
        param node_id: zigbee parent node id of device
        return: Any of _WiserSmartValve, _WiserRoomStat, _WiserHeatingActuator, _WiserUFHController, _WiserSmartPlug, _WiserLight, _WiserDimmableLight, _WiserShutter objects
        """
        try:
            return [device for device in self.all if device.parent_node_id == node_id]
        except IndexError:
            return None
