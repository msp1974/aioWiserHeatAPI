"""
Module to manage all devices
"""

from dataclasses import dataclass
from typing import Any

from .binary_sensor import (
    _WiserBinarySensor,
    _WiserBinarySensorCollection,
)
from .boiler_interface import _WiserBoilerInterface, _WiserBoilerInterfaceCollection
from .button_panel import _WiserButtonPanel, _WiserButtonPanelCollection
from .const import (
    WISERBINARYSENSOR,
    WISERBOILERINTERFACE,
    WISERBUTTONPANEL,
    WISERHEATINGACTUATOR,
    WISERLIGHT,
    WISERPOWERTAGCONTROL,
    WISERPOWERTAGENERGY,
    WISERROOMSTAT,
    WISERSHUTTER,
    WISERSMARTPLUG,
    WISERSMARTVALVE,
    WISERSMOKEALARM,
    WISERTHRESHOLDSENSOR,
    WISERUFHCONTROLLER,
    WISERUICONFIGURATION,
    WISEREQUIPMENT,
)
from .heating_actuator import _WiserHeatingActuator, _WiserHeatingActuatorCollection
from .helpers.device import _WiserDevice
from .helpers.threshold import (
    _WiserThresholdSensor,
)
from .helpers.uiconfiguration import _WiserUIConfigSensor
from .light import _WiserDimmableLight, _WiserLight, _WiserLightCollection
from .ptc import _WiserPowerTagControl, _WiserPowerTagControlCollection
from .pte import _WiserPowerTagEnergy, _WiserPowerTagEnergyCollection
from .rest_controller import _WiserRestController
from .roomstat import _WiserRoomStat, _WiserRoomStatCollection
from .schedule import WiserScheduleTypeEnum, _WiserScheduleCollection
from .shutter import _WiserShutter, _WiserShutterCollection
from .smartplug import _WiserSmartPlug, _WiserSmartPlugCollection
from .smartvalve import _WiserSmartValve, _WiserSmartValveCollection
from .smokealarm import _WiserSmokeAlarm, _WiserSmokeAlarmCollection
from .temp_humidity import _WiserTempHumidity, _WiserTempHumidityCollection
from .ufh import _WiserUFHController, _WiserUFHControllerCollection
from .equipments import _WiserEquipments, _WiserEquipmentsCollection

@dataclass(frozen=True, kw_only=True)
class DeviceConfig:
    device_class: Any
    collection: Any
    endpoint: str = None
    heating: bool = False
    schedule_type: WiserScheduleTypeEnum | None = None
    has_v2_equipment: bool = False


@dataclass(frozen=True, kw_only=True)
class AncillaryDeviceConfig:
    device_class: Any
    attribute: str
    endpoint: str = None


PRODUCT_TYPE_CONFIG = {
    "SmartValve": DeviceConfig(
        device_class=_WiserSmartValve,
        collection=_WiserSmartValveCollection,
        endpoint=WISERSMARTVALVE,
        heating=True,
    ),
    "RoomStat": DeviceConfig(
        device_class=_WiserRoomStat,
        collection=_WiserRoomStatCollection,
        endpoint=WISERROOMSTAT,
        heating=True,
    ),
    "SmartPlug": DeviceConfig(
        device_class=_WiserSmartPlug,
        collection=_WiserSmartPlugCollection,
        endpoint=WISERSMARTPLUG,
        schedule_type=WiserScheduleTypeEnum.onoff,
        has_v2_equipment=True,
    ),
    "HeatingActuator": DeviceConfig(
        device_class=_WiserHeatingActuator,
        collection=_WiserHeatingActuatorCollection,
        endpoint=WISERHEATINGACTUATOR,
        heating=True,
        has_v2_equipment=True,
    ),
    "UnderFloorHeating": DeviceConfig(
        device_class=_WiserUFHController,
        collection=_WiserUFHControllerCollection,
        endpoint=WISERUFHCONTROLLER,
        heating=True,
    ),
    "Light": DeviceConfig(
        device_class=_WiserLight,
        collection=_WiserLightCollection,
        endpoint=WISERLIGHT,
        schedule_type=WiserScheduleTypeEnum.level,
    ),
    "Shutter": DeviceConfig(
        device_class=_WiserShutter,
        collection=_WiserShutterCollection,
        endpoint=WISERSHUTTER,
        schedule_type=WiserScheduleTypeEnum.level,
    ),
    "PTC": DeviceConfig(
        device_class=_WiserPowerTagControl,
        collection=_WiserPowerTagControlCollection,
        endpoint=WISERPOWERTAGCONTROL,
        has_v2_equipment=True,
    ),
    "PTE": DeviceConfig(
        device_class=_WiserPowerTagEnergy,
        collection=_WiserPowerTagEnergyCollection,
        endpoint=WISERPOWERTAGENERGY,
        has_v2_equipment=True,
    ),
    "SmokeAlarmDevice": DeviceConfig(
        device_class=_WiserSmokeAlarm,
        collection=_WiserSmokeAlarmCollection,
        endpoint=WISERSMOKEALARM,
    ),
    "BinarySensor": DeviceConfig(
        device_class=_WiserBinarySensor,
        collection=_WiserBinarySensorCollection,
        endpoint=WISERBINARYSENSOR,
    ),
    "BoilerInterface": DeviceConfig(
        device_class=_WiserBoilerInterface,
        collection=_WiserBoilerInterfaceCollection,
        endpoint=WISERBOILERINTERFACE,
    ),
    "ButtonPanel": DeviceConfig(
        device_class=_WiserButtonPanel,
        collection=_WiserButtonPanelCollection,
        endpoint=WISERBUTTONPANEL,
    ),
    "TempHumidity": DeviceConfig(
        device_class=_WiserTempHumidity,
        collection=_WiserTempHumidityCollection,
        endpoint=None,
    ),
}


ANCILLARY_SENSOR_CONFIG = {
    "ThresholdSensor": AncillaryDeviceConfig(
        device_class=_WiserThresholdSensor,
        attribute="_threshold_sensors",
        endpoint=WISERTHRESHOLDSENSOR,
    ),
    "UIConfiguration": AncillaryDeviceConfig(
        device_class=_WiserUIConfigSensor,
        attribute="_uiconfig_sensors",
        endpoint=WISERUICONFIGURATION,
    ),
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

    def _get_device_info_by_id(self, device_id: int) -> dict[str, Any] | None:
        """Get device entry by id."""
        for device in self._domain_data.get("Device"):
            if device.get("id") == device_id:
                return device
        return None

    def _build(self):
        """Updated builf collection of devices.

        Starts with device type key first and then gets matching device data
        """
        # TODO - limit checks based on DeviceCapabilityMatrix
        for device_type in PRODUCT_TYPE_CONFIG:
            # If not yet in the collection, add empty collection to device collections.
            if device_type not in self._device_collection:
                self._device_collection[device_type] = PRODUCT_TYPE_CONFIG[
                    device_type
                ].collection()

            if device_type == "TempHumidity":
                # This is a workaround for temp humidity device(s)
                for device in self._domain_data.get("Device"):
                    if device.get("ProductType") == "TemperatureHumiditySensor":
                        device_config = PRODUCT_TYPE_CONFIG[device_type]
                        device_class = device_config.device_class
                        self._device_collection[device_type]._items.append(
                            device_class(
                                self._wiser_rest_controller,
                                device_config.endpoint,
                                device,
                                {},
                                None,
                            )
                        )

            elif device_type_data := self._domain_data.get(device_type):
                # We have this device type in data
                device_config = PRODUCT_TYPE_CONFIG[device_type]

                # Now build collection of devices
                for device in device_type_data:
                    # Get class to create and collection to append for device
                    device_class = device_config.device_class

                    # TODO: Fix this so not fudged
                    if device_type == "Light" and device.get("IsDimmable"):
                        device_class = _WiserDimmableLight

                    # Device info id can be DeviceId or id depending on device type
                    device_info_id = device.get("DeviceId", device.get("id"))

                    # Get device info data
                    device_info_data = self._get_device_info_by_id(device_info_id)

                    # If heating device add room id
                    if device_config.heating:
                        if not device.get("RoomId", device_info_data.get("RoomId")):
                            device["RoomId"] = self._get_temp_device_room_id(
                                self._domain_data, device_info_id
                            )

                    # If schedule device add schedule
                    if device_config.schedule_type:
                        device_schedule = self._schedules.get_by_id(
                            device_config.schedule_type, device.get("ScheduleId")
                        )
                    else:
                        device_schedule = None

                    # If has equipment data add to device info
                    if equipment_id := device.get("EquipmentId"):
                        device["EquipmentData"] = self._get_equipment_data(equipment_id)

                    # Add device to collection
                    self._device_collection[device_type]._items.append(
                        device_class(
                            self._wiser_rest_controller,
                            device_config.endpoint,
                            device_info_data,
                            device,
                            device_schedule,
                        )
                    )

        # Add ancillary sensors to device
        for anc_device_type, anc_device_type_info in ANCILLARY_SENSOR_CONFIG.items():
            if anc_device_type_data := self._domain_data.get(anc_device_type):
                for anc_device in anc_device_type_data:
                    device_id = anc_device.get("DeviceId", anc_device.get("id"))
                    if device := self.get_by_id(device_id):
                        if hasattr(device, anc_device_type_info.attribute):
                            getattr(device, anc_device_type_info.attribute).append(
                                anc_device_type_info.device_class(
                                    self._wiser_rest_controller,
                                    anc_device_type_info.endpoint,
                                    anc_device,
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
        try:
            return self._device_collection["HeatingActuator"]
        except KeyError:
            return None

    @property
    def lights(self) -> _WiserLightCollection:
        """Return all lights"""
        try:
            return self._device_collection["Light"]
        except KeyError:
            return None

    @property
    def power_tags_c(self) -> _WiserPowerTagControlCollection:
        """Return all power tag Cs"""
        try:
            return self._device_collection["PTC"]
        except KeyError:
            return None

    @property
    def power_tags(self) -> _WiserPowerTagEnergyCollection:
        """Return all power tags"""
        try:
            return self._device_collection["PTE"]
        except KeyError:
            return None

    @property
    def roomstats(self) -> _WiserRoomStatCollection:
        """Return all roomstats"""
        try:
            return self._device_collection["RoomStat"]
        except KeyError:
            return None

    @property
    def shutters(self) -> _WiserShutterCollection:
        """Return all shutters"""
        try:
            return self._device_collection["Shutter"]
        except KeyError:
            return None

    @property
    def smartplugs(self) -> _WiserSmartPlugCollection:
        """Return all smart plugs"""
        try:
            return self._device_collection["SmartPlug"]
        except KeyError:
            return None

    @property
    def smartvalves(self) -> _WiserSmartValveCollection:
        """Return all smart valves (iTRVs)"""
        try:
            return self._device_collection["SmartValve"]
        except KeyError:
            return None

    @property
    def smokealarms(self) -> _WiserSmokeAlarmCollection:
        """Return all smoke alarms"""
        try:
            return self._device_collection["SmokeAlarmDevice"]
        except KeyError:
            return None

    @property
    def ufh_controllers(self) -> _WiserUFHControllerCollection:
        """Return all UFH controllers"""
        try:
            return self._device_collection["UnderFloorHeating"]
        except KeyError:
            return None

    @property
    def binary_sensor(self):
        """Return all binary sensors"""
        try:
            return self._device_collection["BinarySensor"]
        except KeyError:
            return None

    @property
    def equipments(self):
        """Return all equipments"""
        try:
            return self._device_collection["Equipments"]
        except KeyError:
            return None

    @property
    def temp_humidity_sensors(self):
        """Return all temp humidity sensors"""
        try:
            return self._device_collection["TempHumidity"]
        except KeyError:
            return None

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
