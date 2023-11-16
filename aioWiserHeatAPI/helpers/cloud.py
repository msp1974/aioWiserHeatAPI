from ..const import TEXT_UNKNOWN


class _WiserCloud:
    """Data structure for cloud information for a Wiser Hub"""

    def __init__(self, cloud_status: str, data: dict):
        self._cloud_status = cloud_status
        self._data = data

    @property
    def api_host(self) -> str:
        """Get the host name of the wiser cloud"""
        return self._data.get("WiserApiHost", TEXT_UNKNOWN)

    @property
    def block_publishing(self) -> dict:
        """Get the list of block publishing values"""
        return self._data.get("BlockPublishing", {})

    @property
    def bootstrap_api_host(self) -> str:
        """Get the bootstrap host name of the wiser cloud"""
        return self._data.get("BootStrapApiHost", TEXT_UNKNOWN)

    @property
    def connected_to_cloud(self) -> bool:
        """Get the hub connection status to the wiser cloud"""
        return True if self._cloud_status == "Connected" else False

    @property
    def connection_status(self) -> str:
        """Get the hub cloud connection status text"""
        return self._cloud_status

    @property
    def detailed_publishing_enabled(self) -> bool:
        """Get if detailed published is enabled"""
        return self._data.get("DetailedPublishing", False)

    @property
    def diagnostic_telemetry_enabled(self) -> bool:
        """Get if diagnostic telemetry is enabled"""
        return self._data.get("EnableDiagnosticTelemetry", False)

    @property
    def enable_full_schedule_telemetry(self) -> bool:
        """Get if schedule telemetry enabled"""
        return self._data.get("EnableFullScheduleTelemetry", False)

    @property
    def fio_is_registered(self) -> bool:
        """Get if FIO is registered"""
        return self._data.get("EnableFullScheduleTelemetry", False)
