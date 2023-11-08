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
