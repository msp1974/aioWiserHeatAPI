class _WiserHubCapabilitiesInfo:
    """Data structure for capabilities info for Wiser Hub"""

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
