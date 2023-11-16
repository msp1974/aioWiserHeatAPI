import enum

# Temperature Constants
DEFAULT_AWAY_MODE_TEMP = 10.5
DEFAULT_DEGRADED_TEMP = 18
DEFAULT_BOOST_DELTA = 2
MAX_BOOST_INCREASE = 5
TEMP_ERROR = 2000
TEMP_MINIMUM = 5
TEMP_MAXIMUM = 30
TEMP_HW_ON = 110
TEMP_HW_OFF = -20
TEMP_OFF = -20


# Battery Constants
ROOMSTAT_MIN_BATTERY_LEVEL = 1.7
ROOMSTAT_FULL_BATTERY_LEVEL = 2.7
TRV_FULL_BATTERY_LEVEL = 3.0
TRV_BATTERY_LEVEL_MAPPING = {
    3.0: 100,
    2.9: 80,
    2.8: 60,
    2.7: 40,
    2.6: 20,
    2.5: 10,
    2.4: 5,
    2.3: 0,
}


# Other Constants
REST_BACKOFF_FACTOR = 1
REST_RETRIES = 3
REST_TIMEOUT = 10

# Text Values
TEXT_AUTO = "Auto"
TEXT_BOOST = "Boost"
TEXT_CLOSE = "Close"
TEXT_DEGREESC = "DegreesC"
TEXT_HEATING = "Heating"
TEXT_LEVEL = "Level"
TEXT_LIGHTING = "Lighting"
TEXT_MANUAL = "Manual"
TEXT_NO_CHANGE = "NoChange"
TEXT_OFF = "Off"
TEXT_ON = "On"
TEXT_ONOFF = "OnOff"
TEXT_OPEN = "Open"
TEXT_PASSIVE = "Passive"
TEXT_SETPOINT = "Setpoint"
TEXT_SHUTTERS = "Shutters"
TEXT_STATE = "State"
TEXT_TEMP = "Temp"
TEXT_TIME = "Time"
TEXT_UNKNOWN = "Unknown"
TEXT_WEEKDAYS = "Weekdays"
TEXT_WEEKENDS = "Weekends"
TEXT_ALL = "All"

# Day Value Lists
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
WEEKENDS = ["Saturday", "Sunday"]
SPECIAL_DAYS = [TEXT_WEEKDAYS, TEXT_WEEKENDS, TEXT_ALL]
SPECIAL_TIMES = {"Sunrise": 3000, "Sunset": 4000}


# Wiser Hub Rest Api URL Constants
WISERHUBURL = "http://{}:{}/data/v2/"
WISERHUBDOMAIN = WISERHUBURL + "domain/"
WISERHUBNETWORK = WISERHUBURL + "network/"
WISERHUBSCHEDULES = WISERHUBURL + "schedules/"
WISERHUBOPENTHERM = WISERHUBURL + "opentherm/"
WISERHUBSTATUS = WISERHUBURL + "status/"
WISERSYSTEM = "System"
WISERDEVICE = "Device/{}"
WISERHOTWATER = "HotWater/{}"
WISERROOM = "Room/{}"
WISERSMARTVALVE = "SmartValve/{}"
WISERROOMSTAT = "RoomStat/{}"
WISERSMARTPLUG = "SmartPlug/{}"
WISERHEATINGACTUATOR = "HeatingActuator/{}"
WISERUFHCONTROLLER = "UnderFloorHeating/{}"
WISERSHUTTER = "Shutter/{}"
WISERLIGHT = "Light/{}"
WISERPOWERTAGENERGY = "PTE/{}"


# Enums
class WiserUnitsEnum(enum.Enum):
    imperial = "imperial"
    metric = "metric"


class WiserTempLimitsEnum(enum.Enum):
    heating = {"min": 5, "max": 30, "off": -20, "type": "range"}
    current = {"min": -19, "max": 99, "off": -20, "type": "range"}
    hotwater = {"on": 110, "off": -20, "type": "onoff"}
    boostDelta = {"min": 0, "max": 5, "type": "range"}
    floorHeatingMin = {"min": 5, "max": 39, "off": -20, "type": "range"}
    floorHeatingMax = {"min": 5, "max": 40, "off": -20, "type": "range"}
    floorHeatingOffset = {"min": -9, "max": 9, "type": "range"}


class WiserAwayActionEnum(enum.Enum):
    off = TEXT_OFF
    nochange = TEXT_NO_CHANGE


class WiserShutterAwayActionEnum(enum.Enum):
    close = TEXT_CLOSE
    nochange = TEXT_NO_CHANGE


class WiserDeviceModeEnum(enum.Enum):
    auto = TEXT_AUTO
    manual = TEXT_MANUAL


class WiserHeatingModeEnum(enum.Enum):
    off = TEXT_OFF
    auto = TEXT_AUTO
    manual = TEXT_MANUAL


class WiserPresetOptionsEnum(enum.Enum):
    advance_schedule = "Advance Schedule"
    cancel_overrides = "Cancel Overrides"
    boost30 = "Boost 30m"
    boost60 = "Boost 1h"
    boost120 = "Boost 2h"
    boost180 = "Boost 3h"


WISER_BOOST_DURATION = {
    "Boost 30m": 30,
    "Boost 1h": 60,
    "Boost 2h": 120,
    "Boost 3h": 180,
}


class WiserScheduleTypeEnum(enum.Enum):
    heating = TEXT_HEATING
    onoff = TEXT_ONOFF
    level = TEXT_LEVEL
    lighting = TEXT_LIGHTING
    shutters = TEXT_SHUTTERS


DEFAULT_LEVEL_SCHEDULE = {
    "Monday": {"Time": [], "Level": []},
    "Tuesday": {"Time": [], "Level": []},
    "Wednesday": {"Time": [], "Level": []},
    "Thursday": {"Time": [], "Level": []},
    "Friday": {"Time": [], "Level": []},
    "Saturday": {"Time": [], "Level": []},
    "Sunday": {"Time": [], "Level": []},
}
