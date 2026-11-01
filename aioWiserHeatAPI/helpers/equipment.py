"""
Handles equipment data
"""

from ..const import TEXT_UNKNOWN


class _WiserEquipmentPowerInfo:
    def __init__(self, data: dict):
        self._data = data

    @property
    def current_summation_delivered(self) -> int:
        """Get delivered power"""
        return self._data.get("CurrentSummationDelivered", None)

    @property
    def current_summation_received(self) -> int:
        """Get received power"""
        return self._data.get("CurrentSummationReceived", None)

    @property
    def total_active_power(self) -> int:
        """Get total active power"""
        return self._data.get("TotalActivePower", None)

    @property
    def active_power(self) -> int:
        """Get active power"""
        return self._data.get("ActivePower", None)

    @property
    def rms_current(self) -> int:
        """Get rms current"""
        return self._data.get("RMSCurrent", None)

    @property
    def rms_voltage(self) -> int:
        """Get rms voltage"""
        return self._data.get("RMSVoltage", None)


#  Add for a notification feature Notification if the   Power is under or over a threshold
#  for  a time (periodmins)...
class _WiserEquipmentUnderPowerNotificationInfo(object):
    def __init__(self, data: dict):
        self._data = data

    @property
    def period_mins(self) -> int:
        """Get delivered power"""
        return self._data.get("PeriodMins", 0)

    @property
    def limit(self) -> int:
        """Get limit"""
        return self._data.get("Limit", 0)

    @property
    def enabled(self) -> bool:
        """Get status enable"""
        return self._data.get("Enabled", False)


class _WiserEquipmentOverPowerNotificationInfo:
    def __init__(self, equipment_instance, data: dict):
        self._data = data
        self._equipment_instance = equipment_instance

    @property
    def period_mins(self) -> int:
        """Get period in minutes"""
        return self._data.get("PeriodMins") if self._data.get("PeriodMins") else None

    @property
    def limit(self) -> int:
        """Get limit"""
        return self._data.get("Limit", 100000) if self._data.get("Limit") else None

    @property
    def enabled(self) -> bool:
        """Get status enable"""
        return self._data.get("Enabled", False) if self._data.get("Enabled") else None


class _WiserEquipment:
    """Class to hold equipment object"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def id(self) -> int:
        """Get equipment id"""
        return self._data.get("id", 0)

    @property
    def device_id(self) -> int:
        """Get device id"""
        return self._data.get("DeviceApplicationInstanceId", 0)

    @property
    def device_type(self) -> str:
        """Get device id"""
        return self._data.get("DeviceApplicationInstanceType", TEXT_UNKNOWN)

    @property
    def uuid(self) -> str:
        """Get UUID"""
        return self._data.get("UUID", TEXT_UNKNOWN)

    @property
    def controllable(self) -> bool:
        """Get if controllable"""
        return self._data.get("Controllable", False)

    @property
    def cloud_managed(self) -> bool:
        """Get if cloud managed"""
        return self._data.get("CloudManaged", False)

    @property
    def monitored(self) -> bool:
        """Get if monitored"""
        return self._data.get("Monitored", False)

    @property
    def smart_compatible(self) -> bool:
        """Get if smart compatible"""
        return self._data.get("SmartCompatible", False)

    @property
    def smart_supported(self) -> bool:
        """Get if smart supported"""
        return self._data.get("SmartSupported", False)

    @property
    def can_be_scheduled(self) -> bool:
        """Get if can be scheduled"""
        return self._data.get("CanBeScheduled", False)

    @property
    def onoff_green_schedule_supported(self) -> bool:
        """Get if OnOff green schedule supported"""
        return self._data.get("OnOffGreenScheduleSupported", False)

    @property
    def onoff_cost_schedule_supported(self) -> bool:
        """Get if OnOff cost schedule supported"""
        return self._data.get("OnOffCostScheduleSupported", False)

    @property
    def number_of_phases(self) -> str:
        """Get number of phases"""
        return self._data.get("NumberOfPhases", TEXT_UNKNOWN)

    @property
    def configured(self) -> str:
        """Get if configured"""
        return self._data.get("Configured", TEXT_UNKNOWN)

    @property
    def installation_type(self) -> str:
        """Get installation_type"""
        return self._data.get("InstallationType", TEXT_UNKNOWN)

    @property
    def equipment_family(self) -> str:
        """Get equipment family"""
        return self._data.get("EquipmentFamily", TEXT_UNKNOWN)

    @property
    def equipment_name(self) -> str:
        """Get equipment name"""
        return self._data.get("EquipmentName", TEXT_UNKNOWN)

    @property
    def product_type(self) -> str:
        """Get equipment name"""
        return self._data.get("ProductType", TEXT_UNKNOWN)

    @property
    def functional_control_mode(self) -> str:
        """Get functional control mode"""
        return self._data.get("FunctionalControlMode", TEXT_UNKNOWN)

    @property
    def current_control_mode(self) -> str:
        """Get current control mode"""
        return self._data.get("CurrentControlMode", TEXT_UNKNOWN)

    @property
    def load_state_status(self) -> str:
        """Get load state status"""
        return self._data.get("LoadStateStatus", TEXT_UNKNOWN)

    @property
    def load_state_command_optimized(self) -> str:
        """Get load state command optimized"""
        return self._data.get("LoadStateCommandOptimized", TEXT_UNKNOWN)

    @property
    def load_shedding_status(self) -> str:
        """Get load shedding status"""
        return self._data.get("LoadSheddingStatus", TEXT_UNKNOWN)

    @property
    def load_state_command_prio(self) -> str:
        """Get load state command prio"""
        return self._data.get("LoadStateCommandPrio", TEXT_UNKNOWN)

    @property
    def load_setpoint_command_prio(self) -> int:
        """Get load setpoint command prio"""
        return self._data.get("LoadSetpointCommandPrio", None)

    @property
    def pcm_mode(self) -> bool:
        """Get Pcm Mode"""
        return self._data.get("PcmMode", False)

    @property
    def pcm_supported(self) -> bool:
        """Get Pcm supported"""
        return self._data.get("PcmSupported", False)

    @property
    def pcm_priority(self) -> int:
        """Get Pcm priority"""
        return self._data.get("PcmPriority", None)

    @property
    def direction(self) -> str:
        """Get flow direction"""
        return self._data.get("Direction", TEXT_UNKNOWN)

    @property
    def operating_status(self) -> str:
        """Get the operating status"""
        return self._data.get("OperatingStatus", TEXT_UNKNOWN)

    @property
    def fault_status(self) -> str:
        """Get the fault status"""
        return self._data.get("FaultStatus", TEXT_UNKNOWN)

    @property
    def power(self) -> _WiserEquipmentPowerInfo:
        """Get the power info"""
        return _WiserEquipmentPowerInfo(self._data)

    #  Add for a notification feature Notification if the   Power is under or over a threshold
    #  for  a time (periodmins)...
    @property
    def under_power_notification(self) -> _WiserEquipmentUnderPowerNotificationInfo:
        """Get notification info"""
        return (
            _WiserEquipmentUnderPowerNotificationInfo(
                self._data.get("UnderPowerNotification")
            )
            if self._data.get("UnderPowerNotification")
            else None
        )

    @property
    def over_power_notification(self) -> _WiserEquipmentOverPowerNotificationInfo:
        """Get notification info"""
        return (
            _WiserEquipmentUnderPowerNotificationInfo(
                self._data.get("OverPowerNotification")
            )
            if self._data.get("OverPowerNotification")
            else None
        )
