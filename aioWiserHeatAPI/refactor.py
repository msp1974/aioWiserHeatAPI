# Manufacturers
from dataclasses import dataclass
from functools import reduce
from typing import Any

DRAYTON = "Drayton Wiser"
SCHNEIDER = "Schneider Electric"
MERTON = "Merton"

# ScheduleTypes
ONOFF = "OnOff"
LEVEL = "Level"
HEATING = "Heating"


@dataclass
class DeviceDataKeys:
    """Class to hold data keys to add to devices."""

    device_data: str | None = None
    additional_data: str | None = None
    manufacturer: str = DRAYTON
    schedule_type: str | None = None

SUPPORTEDDEVICES = {
    "RoomStat": DeviceDataKeys("RoomStat"),
    "SmartValve": DeviceDataKeys("iTRV"),
    
}

DEVICEMATRIX = {
    "Controller": DeviceDataKeys(
        additional_data=[
            "System",
            "Cloud",
            "Zigbee",
            "UpgradeInfo",
            "Moment",
            "DeviceCapabilityMatrix",
            "HeatingChannel",
            "HotWater",
        ]
    ),
    "RoomStat": DeviceDataKeys("RoomStat"),
    "iTRV": DeviceDataKeys("SmartValve"),
    "SmartPlug": DeviceDataKeys("SmartPlug", schedule_type=ONOFF),
    "HeatingActuator": DeviceDataKeys("HeatingActuator"),
    "Shutter": DeviceDataKeys("Shutter", manufacturer=SCHNEIDER, schedule_type=LEVEL),
    "DimmableLight": DeviceDataKeys(
        "Light", manufacturer=SCHNEIDER, schedule_type=LEVEL
    ),
    "OnOffLight": DeviceDataKeys("Light", manufacturer=SCHNEIDER, schedule_type=LEVEL),
    "PowerTagE": DeviceDataKeys("PTE", manufacturer=SCHNEIDER),
    "WindowDoorSensor": DeviceDataKeys("BinarySensor", manufacturer=SCHNEIDER),
    "BoilerInterface": DeviceDataKeys("BoilerInterface"),
    "UnderFloorHeating": DeviceDataKeys("UnderFloorHeating"),
    "CFMT": DeviceDataKeys(
        "HeatingActuator",
        additional_data=["ThresholdSensor", "UIConfiguration"],
        manufacturer=MERTON,
    ),
    "SmokeAlarmDevice": DeviceDataKeys("SmokeAlarmDevice", manufacturer=SCHNEIDER),
}


def get_key(
    dot_notation_path: str, data: dict
) -> dict[str, dict | str | int] | str | int:
    """Try to get a deep value from a dict based on a dot-notation."""
    if dot_notation_path == "":
        return data

    if dot_notation_path is None:
        return None

    try:
        return reduce(dict.get, dot_notation_path.split("."), data)
    except (TypeError, KeyError):
        return None


def get_device_class_data_by_device_id(
    device_class: str, device_id: int, data: dict[str, Any]
) -> dict[str, Any]:
    """Get device class (type) data by device id."""
    class_devices = get_key(f"Domain.{device_class}", data)
    for device in class_devices:
        if device.get("DeviceId", device.get("id")) == device_id:
            return device


def get_room_name(room_id: int, data: dict[str, Any]) -> str:
    """Get room name by room id."""
    rooms = get_key("Domain.Room", data)
    for room in rooms:
        if room.get("id") == room_id:
            return room.get("Name")


def get_room_id_for_device(device_id: int, data: dict[str, Any]) -> int:
    """Find room id for device - specifically for v1 hub."""
    rooms = get_key("Domain.Room", data)
    for room in rooms:
        if (
            device_id in room.get("SmartValveIds", [])
            or device_id in room.get("UfhRelayIds", [])
            or device_id == room.get("RoomStatId")
        ):
            return room.get("id")
    return 0


def get_schedule_by_id(
    schedule_type: str, schedule_id: int, data: dict[str, Any]
) -> dict[str, Any] | None:
    """Get schedule by type and id."""
    schedules = data.get("Schedule", {}).get(schedule_type)
    if schedules:
        for schedule in schedules:
            if schedule.get("id") == schedule_id:
                schedule["ScheduleClass"] = schedule_type
                return schedule
    return None


def generate_device_name(
    device: dict[str, Any], data: dict[str, Any], force_room: bool = False
) -> str:
    """Generate name for device.

    If has a name attribute - return that
    If belongs to a room - return product_type and room name
    Otherwise return device_type and id
    """
    attributes = device.get("DeviceAttributes")

    if not force_room:
        if name := attributes.get("Name"):
            return name
    if room_id := attributes.get("RoomId"):
        room_name = get_room_name(room_id, data)
        return f"{device.get('ProductType')} {room_name}"
    return f"{device.get('ProductType')} {attributes.get('id')}"


def refactor(data: dict[str, Any]):
    """Refactor and output data."""

    # Add device name

    result = {"Domain": {}}

    # Iterate devices
    result["Domain"].update({"Device": {}})
    for device in get_key("Domain.Device", data):
        print(f"DEVICE: {device.get("ProductType")}")
        data_keys = DEVICEMATRIX.get(device.get("ProductType"))
        device_id = device.get("id")

        # Add manufacturer
        device["ProductManufacturer"] = (
            data_keys.manufacturer
            if data_keys and hasattr(data_keys, "manufacturer")
            else "Schenider Electric"
        )

        # Add device data
        if data_keys.device_data:
            device["DeviceAttributes"] = get_device_class_data_by_device_id(
                data_keys.device_data, device_id, data
            )

            # Ensure room id.
            if not device["DeviceAttributes"].get("RoomId"):
                room_id = get_room_id_for_device(device_id, data)
                if room_id:
                    device["DeviceAttributes"]["RoomId"] = room_id

            device["DeviceAttributes"]["DeviceClass"] = data_keys.device_data

            # Add schedule
            if data_keys.schedule_type and device["DeviceAttributes"].get("ScheduleId"):
                device["DeviceSchedule"] = get_schedule_by_id(
                    data_keys.schedule_type,
                    device["DeviceAttributes"].get("ScheduleId"),
                    data,
                )

        # Add name
        if device_id == 0:
            device["DeviceName"] = get_key(
                "Network.AccessPoint.NetworkInterface.HostName", data
            )
        else:
            device["DeviceName"] = generate_device_name(device, data)

        # Add additional data
        if data_keys.additional_data:
            additional_keys = data_keys.additional_data
            if not isinstance(additional_keys, list):
                additional_keys = [additional_keys]

            for add_key in additional_keys:
                add_key_data = get_key(f"Domain.{add_key}", data)

                if isinstance(add_key_data, list):
                    # refactor to key:value using id
                    refactored = {}
                    for entry in add_key_data:
                        refactored[entry.get("id")] = entry
                    add_key_data = refactored

                if add_key_data:
                    device[add_key] = add_key_data

        result["Domain"]["Device"][device.get("id")] = device

    # Add rooms
    result["Domain"].update({"Room": {}})
    rooms = get_key("Domain.Room", data)
    for room in rooms:
        if schedule_id := room.get("ScheduleId"):
            room["RoomSchedule"] = get_schedule_by_id(HEATING, schedule_id, data)

        result["Domain"]["Room"][room.get("id")] = room

    # Network
    result["Domain"]["Device"][0]["Network"] = data.get("Network")

    result["Domain"]["Device"][0]["Status"] = data.get("Status")

    return result
