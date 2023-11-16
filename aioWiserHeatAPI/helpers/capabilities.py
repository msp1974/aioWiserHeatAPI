"""
Handles hub capabilities
"""


class _WiserHubCapabilitiesInfo:
    """Data structure for device capabilities info for Wiser Hub"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def all(self) -> dict:
        "Get the list of capabilities"
        return dict(self._data)

    @property
    def smartplug(self) -> bool:
        return self._data.get("SmartPlug", False)

    @property
    def itrv(self) -> bool:
        return self._data.get("ITRV", False)

    @property
    def roomstat(self) -> bool:
        return self._data.get("Roomstat", False)

    @property
    def ufh(self) -> bool:
        return self._data.get("UFH", False)

    @property
    def ufh_floor_temp_sensor(self) -> bool:
        return self._data.get("UFHFloorTempSensor", False)

    @property
    def ufh_dew_sensor(self) -> bool:
        return self._data.get("UFHDewSensor", False)

    @property
    def hact(self) -> bool:
        return self._data.get("HACT", False)

    @property
    def lact(self) -> bool:
        return self._data.get("LACT", False)

    @property
    def light(self) -> bool:
        return self._data.get("Light", False)

    @property
    def shutter(self) -> bool:
        return self._data.get("Shutter", False)

    @property
    def load_controller(self) -> bool:
        return self._data.get("LoadController", False)

    # Hub V2 additional capabilities

    @property
    def smart_socket(self) -> bool:
        return self._data.get("SmartSocket", False)

    @property
    def two_gang_lights(self) -> bool:
        return self._data.get("TwoGangLights", False)

    @property
    def fls(self) -> bool:
        return self._data.get("FLS", False)

    @property
    def boiler_interfce(self) -> bool:
        return self._data.get("BoilerInterface", False)

    @property
    def window_door_sensor(self) -> bool:
        return self._data.get("WindowDoorSensor", False)

    @property
    def motion_light_sensor(self) -> bool:
        return self._data.get("MotionLightSensor", False)

    @property
    def water_leakage_sensor(self) -> bool:
        return self._data.get("WaterLeakageSensor", False)

    @property
    def temperature_humidity_sensor(self) -> bool:
        return self._data.get("TemperatureHumiditySensor", False)

    @property
    def power_tag_e(self) -> bool:
        return self._data.get("PowerTagE", False)

    @property
    def cfmt(self) -> bool:
        return self._data.get("CFMT", False)

    @property
    def evse(self) -> bool:
        return self._data.get("EVSE", False)

    @property
    def smoke_alarm(self) -> bool:
        return self._data.get("SmokeAlarmDevice", False)

    @property
    def air_zone(self) -> bool:
        return self._data.get("Airzone", False)

    @property
    def nod_on_puck(self) -> bool:
        return self._data.get("NodOnPuck", False)

    @property
    def nod_on_16_puck(self) -> bool:
        return self._data.get("NodOn16APuck", False)

    @property
    def ev_socket(self) -> bool:
        return self._data.get("EVSocket", False)

    @property
    def fil_pilote_puck(self) -> bool:
        return self._data.get("FilPilotePuck", False)

    @property
    def iconic_devices(self) -> bool:
        return self._data.get("IconicDevices", False)


class _WiserHubAutomationCapabilities:
    """Data structure for automations features (v2 hub)"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def max_actions(self) -> int:
        return self._data.get("MaxActions", 0)

    @property
    def max_triggers(self) -> int:
        return self._data.get("MaxTriggers", 0)

    @property
    def max_constraints(self) -> int:
        return self._data.get("MaxTimeConstraints", 0)


class _WiserHubPTECapabilities:
    """Data structure for PTE features (v2 hub)"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def energy_export(self) -> bool:
        return self._data.get("EnergyExport", False)


class _WiserHubFeatureCapabilitiesInfo:
    """Data structure for feature capabilities info for Wiser Hub"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def all(self) -> dict:
        "Get the list of capabilities"
        return dict(self._data)

    @property
    def automations(self) -> _WiserHubAutomationCapabilities:
        """Get automation capabilities"""
        return _WiserHubAutomationCapabilities(self._data.get("Automation", {}))

    @property
    def pte(self) -> _WiserHubPTECapabilities:
        """Get PTE capabilities"""
        return _WiserHubPTECapabilities(self._data.get("PTE", {}))


class _WiserClimateCapabilities(object):
    """Data structure for climate capalbilities of a room"""

    def __init__(self, room, data: dict):
        self._data = data
        self._room = room

    @property
    def heating_supported(self) -> bool:
        """Get heating supported value"""
        return self._data.get("HeatingSupported")

    @property
    def cooling_supported(self) -> bool:
        """Get cooling supported value"""
        return self._data.get("CoolingSupported")

    @property
    def minimum_heat_set_point(self) -> int:
        """Get minimum heat setpoint value"""
        return self._data.get("MinimumHeatSetpoint")

    @property
    def maximum_heat_set_point(self) -> int:
        """Get maximum heat setpoint value"""
        return self._data.get("MaximumHeatSetpoint")

    @property
    def minimum_cool_set_point(self) -> int:
        """Get minimum cool setpoint value"""
        return self._data.get("MinimumCoolSetpoint")

    @property
    def maximum_cool_set_point(self) -> int:
        """Get maximum cool setpoint value"""
        return self._data.get("MaximumCoolSetpoint")

    @property
    def setpoint_step(self) -> int:
        """Get setpoint step value"""
        return self._data.get("SetpointStep")

    @property
    def ambient_temperature(self) -> bool:
        """Get ambient temperature value"""
        return self._data.get("AmbientTemperature")

    @property
    def temperature_control(self) -> bool:
        """Get temperature control value"""
        return self._data.get("TemperatureControl")

    @property
    def open_window_detection(self) -> bool:
        """Get open window detection value"""
        return self._data.get("OpenWindowDetection")

    @property
    def hydronic_channel_selection(self) -> bool:
        """Get hydronic channel selection value"""
        if self._data:
            return self._data.get("HydronicChannelSelection")
        return None

    @property
    def on_off_supported(self) -> bool:
        """Get on off supported value"""
        if self._data:
            return self._data.get("OnOffSupported")
        return None
