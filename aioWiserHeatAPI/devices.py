"""
Module to manage all devices
"""

import enum

from .binary_sensor import _WiserBinarySensorCollection, _WiserWindowDoorSensor
from .boiler_interface import _WiserBoilerInterface, _WiserBoilerInterfaceCollection
from .button_panel import _WiserButtonPanel, _WiserButtonPanelCollection
from .const import (
    TEXT_UNKNOWN,
    WISERBINARYSENSOR,
    WISERBOILERINTERFACE,
    WISERBUTTONPANEL,
    WISERHEATINGACTUATOR,
    WISERLIGHT,
    WISERPOWERTAGENERGY,
    WISERROOMSTAT,
    WISERSHUTTER,
    WISERSMARTPLUG,
    WISERSMARTVALVE,
    WISERSMOKEALARM,
    WISERUFHCONTROLLER,
)
from .heating_actuator import _WiserHeatingActuator, _WiserHeatingActuatorCollection
from .helpers.device import _WiserDevice
from .light import _WiserDimmableLight, _WiserLight, _WiserLightCollection
from .pte import _WiserPowerTagEnergy, _WiserPowerTagEnergyCollection
from .rest_controller import _WiserRestController
from .roomstat import _WiserRoomStat, _WiserRoomStatCollection
from .schedule import WiserScheduleTypeEnum, _WiserScheduleCollection
from .shutter import _WiserShutter, _WiserShutterCollection
from .smartplug import _WiserSmartPlug, _WiserSmartPlugCollection
from .smartvalve import _WiserSmartValve, _WiserSmartValveCollection
from .smokealarm import _WiserSmokeAlarm, _WiserSmokeAlarmCollection
from .ufh import _WiserUFHController, _WiserUFHControllerCollection


class _WiserDeviceTypeEnum(enum.Enum):
    iTRV = "SmartValve"
    RoomStat = "RoomStat"
    SmartPlug = "SmartPlug"
    HeatingActuator = "HeatingActuator"
    UnderFloorHeating = "UnderFloorHeating"
    Shutter = "Shutter"
    OnOffLight = "Light"
    DimmableLight = "Light"
    PowerTagE = "PTE"
    SmokeAlarmDevice = "SmokeAlarmDevice"
    WindowDoorSensor = "BinarySensor"
    BoilerInterface = "BoilerInterface"
    CFMT = "HeatingActuator"
    ButtonPanel = "ButtonPanel"


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
        "has_v2_equipment": True,
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
        "has_v2_equipment": True,
    },
    "Shutter": {
        "class": _WiserShutter,
        "collection": _WiserShutterCollection,
        "endpoint": WISERSHUTTER,
        "schedule_type": WiserScheduleTypeEnum.level,
    },
    "OnOffLight": {
        "class": _WiserLight,
        "collection": _WiserLightCollection,
        "endpoint": WISERLIGHT,
        "schedule_type": WiserScheduleTypeEnum.level,
    },
    "DimmableLight": {
        "class": _WiserDimmableLight,
        "collection": _WiserLightCollection,
        "endpoint": WISERLIGHT,
        "schedule_type": WiserScheduleTypeEnum.level,
    },
    "PowerTagE": {
        "class": _WiserPowerTagEnergy,
        "collection": _WiserPowerTagEnergyCollection,
        "endpoint": WISERPOWERTAGENERGY,
        "has_v2_equipment": True,
    },
    "SmokeAlarmDevice": {
        "class": _WiserSmokeAlarm,
        "collection": _WiserSmokeAlarmCollection,
        "endpoint": WISERSMOKEALARM,
    },
    "WindowDoorSensor": {
        "class": _WiserWindowDoorSensor,
        "collection": _WiserBinarySensorCollection,
        "endpoint": WISERBINARYSENSOR,
    },
    "BoilerInterface": {
        "class": _WiserBoilerInterface,
        "collection": _WiserBoilerInterfaceCollection,
        "endpoint": WISERBOILERINTERFACE,
    },
    "CFMT": {
        "class": _WiserHeatingActuator,
        "collection": _WiserHeatingActuatorCollection,
        "endpoint": WISERHEATINGACTUATOR,
        "heating": True,
        "has_v2_equipment": True,
    },
    "ButtonPanel": {
        "class": _WiserButtonPanel,
        "collection": _WiserButtonPanelCollection,
        "endpoint": WISERBUTTONPANEL,
    },
}


class _WiserDeviceCollection:
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
        self._equipment_data = domain_data.get("Equipment", {})  # Supported by v2 hub
        self._schedules = schedules
        self._device_collection = {}

        self._build()

    def _get_equipment_data(self, equipment_id: int) -> dict:
        """Get equipment data"""
        equipment_data = [
            equipment_data
            for equipment_data in self._equipment_data
            if equipment_data.get("id") == equipment_id
        ]
        return equipment_data[0] if equipment_data else None

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
                        if device_info.get("DeviceId", device_info.get("id"))
                        == device.get("id")
                    ]

                    # Safety net to prevent error if device info not found
                    if not device_info:
                        continue

                    # Get class to create and collection to append for device
                    device_class = PRODUCT_TYPE_CONFIG[device_type].get("class")

                    # If heating device add room id
                    if device_config.get("heating"):
                        if not device.get("RoomId"):
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

                    # If has equipment entry, add equipment to device info data
                    if device_config.get("has_v2_equipment"):
                        device_info[0]["EquipmentData"] = self._get_equipment_data(
                            device_info[0].get("EquipmentId")
                        )

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
    def all(self) -> list[_WiserDevice]:
        """Return all devices"""
        items = []
        for key in self._device_collection:
            items.extend(self._device_collection[key].all)
        return items

    @property
    def count(self) -> int:
        """Return count of devices"""
        return len(self.all)

    @property
    def heating_actuators(self) -> _WiserHeatingActuatorCollection:
        """Return all heating actuators"""
        return self._device_collection["HeatingActuator"]

    @property
    def lights(self) -> _WiserLightCollection:
        """Return all lights"""
        return self._device_collection["Light"]

    @property
    def power_tags(self) -> _WiserPowerTagEnergyCollection:
        """Return all power tags"""
        return self._device_collection["PTE"]

    @property
    def roomstats(self) -> _WiserRoomStatCollection:
        """Return all roomstats"""
        return self._device_collection["RoomStat"]

    @property
    def shutters(self) -> _WiserShutterCollection:
        """Return all shutters"""
        return self._device_collection["Shutter"]

    @property
    def smartplugs(self) -> _WiserSmartPlugCollection:
        """Return all smart plugs"""
        return self._device_collection["SmartPlug"]

    @property
    def smartvalves(self) -> _WiserSmartValveCollection:
        """Return all smart valves (iTRVs)"""
        return self._device_collection["SmartValve"]

    @property
    def smokealarms(self) -> _WiserSmokeAlarmCollection:
        """Return all smoke alarms"""
        return self._device_collection["SmokeAlarmDevice"]

    @property
    def ufh_controllers(self) -> _WiserUFHControllerCollection:
        """Return all UFH controllers"""
        return self._device_collection["UnderFloorHeating"]

    @property
    def binary_sensor(self):
        """Return all binary sensors"""
        return self._device_collection["BinarySensor"]

    def get_by_id(self, device_id: int) -> _WiserDevice:
        """
        Gets a device object from the devices id
        param id: id of device
        return: Device type class
        """
        try:
            return [device for device in self.all if device.id == device_id][0]
        except IndexError:
            return None

    def get_by_room_id(self, room_id: int) -> list[_WiserDevice]:
        """
        Gets a list of devices belonging to the room id
        param room_id: the id of the room
        return: Device type class
        """
        try:
            return [device for device in self.all if device.room_id == room_id]
        except IndexError:
            return None

    def get_by_node_id(self, node_id: int) -> _WiserDevice:
        """
        Gets a device object from the devices zigbee node id
        param node_id: zigbee node id of device
        return: Device type class
        """
        try:
            return [device for device in self.all if device.node_id == node_id][0]
        except IndexError:
            return None

    def get_by_serial_number(self, serial_number: str) -> _WiserDevice:
        """
        Gets a device object from the devices serial number
        param node_id: serial number of device
        return: Device type class
        """
        try:
            return [
                device for device in self.all if device.serial_number == serial_number
            ][0]
        except IndexError:
            return None

    def get_by_parent_node_id(self, node_id: int) -> list[_WiserDevice]:
        """
        Gets a list of device from the devices zigbee parent node id
        param node_id: zigbee parent node id of device
        return: Device type class
        """
        try:
            return [device for device in self.all if device.parent_node_id == node_id]
        except IndexError:
            return None
