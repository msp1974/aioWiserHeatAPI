from ..rest_controller import _WiserRestController
from ..const import TEXT_UNKNOWN, WISERHUBNETWORK


class _WiserDetectedNetwork:
    """Data structure for detected network"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def ssid(self) -> str:
        return self._data.get("SSID")

    @property
    def channel(self) -> int:
        return self._data.get("Channel")

    @property
    def security_mode(self) -> str:
        return self._data.get("SecurityMode")

    @property
    def rssi(self) -> int:
        return self._data.get("RSSI")


class _WiserNetworkStatistics:
    """Data structure for network statistics"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def ipv4_address_ping(self) -> str:
        return self._data.get("IPv4AddressPing")

    @property
    def healthcheck_enabled(self) -> str:
        return self._data.get("HealthCheckingEnabled")

    @property
    def external_ping_enabled(self) -> str:
        return self._data.get("ExternalPingEnabled")

    @property
    def internal_ping_enabled(self) -> str:
        return self._data.get("InternalPingEnabled")

    @property
    def dns_resolution_enabled(self) -> str:
        return self._data.get("DnsResolutionEnabled")

    @property
    def recovery_actions(self) -> int:
        return self._data.get("RecoveryActions")

    @property
    def external_ping_count(self) -> int:
        return self._data.get("ExternalPing_Count")

    @property
    def internal_ping_count(self) -> int:
        return self._data.get("InternalPing_Count")

    @property
    def internal_ping_failed_count(self) -> int:
        return self._data.get("InternalPingFailed_Count")

    @property
    def dns_resolution_test_count(self) -> int:
        return self._data.get("DnsResolutionTest_Count")

    @property
    def reconnection_fix_count(self) -> int:
        return self._data.get("ReconnectionFix_Count")

    @property
    def wifi_recovery_count(self) -> int:
        return self._data.get("HealthCheckWifiRecovery_Count")

    @property
    def wifi_total_uptime(self) -> int:
        return self._data.get("WifiTotalUptime")

    @property
    def wifi_last_uptime(self) -> int:
        return self._data.get("WifiLastUptime")

    @property
    def wifi_total_downtime(self) -> int:
        return self._data.get("WifiTotalDowntime")

    @property
    def wifi_last_downtime(self) -> int:
        return self._data.get("WifiLastDowntime")

    @property
    def wifi_channel_changes(self) -> int:
        return self._data.get("WifiChannelChanges")

    @property
    def wifi_state_no_error_count(self) -> int:
        return self._data.get("WifiStateNoError_Count")

    @property
    def wifi_state_ap_not_found_count(self) -> int:
        return self._data.get("WifiStateApNotFound_Count")

    @property
    def station_disconnected_count(self) -> int:
        return self._data.get("StationConnected_Count")

    @property
    def station_disconnected_count(self) -> int:
        return self._data.get("StationDisconnected_Count")

    @property
    def cloud_connection_drop_count(self) -> int:
        return self._data.get("CloudConnectionDrop_Count")

    @property
    def station_transition_to_connected_count(self) -> int:
        return self._data.get("StationTransitionToConnected_Count")

    @property
    def station_transition_to_disconencted_count(self) -> int:
        return self._data.get("StationTransitionToDisconnected_Count")


class _WiserNetwork:
    """Data structure for network information for a Wiser Hub"""

    def __init__(self, data: dict, wiser_rest_controller: _WiserRestController):
        self._data = data
        self._dhcp_status = data.get("DhcpStatus", {})
        self._network_interface = data.get("NetworkInterface", {})
        self._detected_access_points = []
        self._wiser_rest_controller = wiser_rest_controller

        for detected_network in self._data.get("DetectedAccessPoints", []):
            self._detected_access_points.append(_WiserDetectedNetwork(detected_network))

    @property
    def detected_access_points(self) -> list:
        return self._detected_access_points

    @property
    def dhcp_mode(self) -> str:
        """Get the current dhcp mode of the hub"""
        return self._data.get("NetworkInterface", {}).get("DhcpMode", TEXT_UNKNOWN)

    @property
    def healthckeck_stats(self) -> _WiserNetworkStatistics:
        """Get the network healthcheck stats of the hub"""
        return _WiserNetworkStatistics(self._data.get("HealthCheckStats", {}))

    @property
    def hostname(self) -> str:
        """Get the host name of the hub"""
        return self._data.get("NetworkInterface", {}).get("HostName", TEXT_UNKNOWN)

    @property
    def ip_address(self) -> str:
        """Get the ip address of the hub"""
        if self.dhcp_mode == "Client":
            return self._dhcp_status.get("IPv4Address", TEXT_UNKNOWN)
        else:
            return self._network_interface.get("IPv4HostAddress", TEXT_UNKNOWN)

    @property
    def ip_subnet_mask(self) -> str:
        """Get the subnet mask of the hub"""
        if self.dhcp_mode == "Client":
            return self._dhcp_status.get("IPv4SubnetMask", TEXT_UNKNOWN)
        else:
            return self._network_interface.get("IPv4SubnetMask", TEXT_UNKNOWN)

    @property
    def ip_gateway(self) -> str:
        """Get the default gateway of the hub"""
        if self.dhcp_mode == "Client":
            return self._dhcp_status.get("IPv4DefaultGateway", TEXT_UNKNOWN)
        else:
            return self._network_interface.get("IPv4DefaultGateway", TEXT_UNKNOWN)

    @property
    def ip_primary_dns(self) -> str:
        """Get the primary dns server of the hub"""
        if self.dhcp_mode == "Client":
            return self._dhcp_status.get("IPv4PrimaryDNS", TEXT_UNKNOWN)
        else:
            return self._network_interface.get("IPv4PrimaryDNS", TEXT_UNKNOWN)

    @property
    def ip_secondary_dns(self) -> str:
        """Get the secondary dns server of the hub"""
        if self.dhcp_mode == "Client":
            return self._dhcp_status.get("IPv4SecondaryDNS", TEXT_UNKNOWN)
        else:
            return self._network_interface.get("IPv4SecondaryDNS", TEXT_UNKNOWN)

    @property
    def mac_address(self) -> str:
        """Get the mac address of the hub wifi interface"""
        return self._data.get("MacAddress", TEXT_UNKNOWN)

    @property
    def signal_percent(self) -> int:
        """Get the wifi signal strength percentage"""
        return min(100, int(2 * (self._data.get("RSSI", {}).get("Current", 0) + 100)))

    @property
    def signal_rssi(self) -> int:
        """Get the wifi signal rssi value"""
        return self._data.get("RSSI", {}).get("Current", 0)

    @property
    def signal_rssi_min(self) -> int:
        """Get the wifi signal min rssi value"""
        return self._data.get("RSSI", {}).get("Min", 0)

    @property
    def signal_rssi_max(self) -> int:
        """Get the wifi signal max rssi value"""
        return self._data.get("RSSI", {}).get("Max", 0)

    @property
    def security_mode(self) -> str:
        """Get the wifi security mode"""
        return self._data.get("SecurityMode", TEXT_UNKNOWN)

    @property
    def ssid(self) -> str:
        """Get the ssid of the wifi network the hub is connected to"""
        return self._data.get("SSID", TEXT_UNKNOWN)

    async def connect_to_network(
        self, ssid: str, password: str, channel: int = None, security_mode: str = None
    ):
        """
        Connect hub to wifi network
        param ssid: wifi network ssid
        param password: wifi password
        param channel: wifi channel (optional)
        param security_mode: wifi security mode (optional)
        return: boolean
        """
        cmd_data = {"Enabled": True}
        if ssid and password:
            cmd_data["SSID"] = ssid
            cmd_data["SecurityKey"] = password

        if channel:
            cmd_data["Channel"] = channel

        if security_mode:
            cmd_data["SecurityMode"] = security_mode

        return await self._wiser_rest_controller._send_command(
            f"{WISERHUBNETWORK}/Station", cmd_data
        )
