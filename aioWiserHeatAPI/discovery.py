import asyncio
from . import _LOGGER

from typing import cast
from zeroconf import ServiceStateChange, IPVersion
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf, AsyncServiceInfo

MDNS_TIMEOUT = 2


class _WiserDiscoveredHub(object):
    def __init__(self, ip: str, hostname: str, name: str):
        self._ip = ip
        self._name = name
        self._hostname = hostname

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def hostname(self) -> str:
        return self._hostname

    @property
    def name(self) -> str:
        return self._name


class WiserDiscovery(object):
    """
    Class to handle mDns discovery of a wiser hub on local network
    Use discover_hub() to return list of mDns responses.
    """

    def __init__(self):
        self._discovered_hubs = []
        self.mdns_timeout = MDNS_TIMEOUT

    @property
    def mdns_timeout(self):
        return self._mdns_timeout

    @mdns_timeout.setter
    def mdns_timeout(self, mdns_timeout):
        self._mdns_timeout = mdns_timeout

    def async_on_service_state_change(
        self,
        zeroconf: AsyncZeroconf,
        service_type: str,
        name: str,
        state_change: ServiceStateChange,
    ) -> None:
        """
        Look for Wiser Hub in discovered services and set IP and Name in
        global vars
        """

        loop = asyncio.get_running_loop()
        loop.create_task(
            self.async_parse_state_change(zeroconf, service_type, name, state_change)
        )

    async def async_parse_state_change(
        self, zeroconf, service_type, name, state_change
    ):

        info = AsyncServiceInfo(service_type, name)

        if state_change != ServiceStateChange.Removed:
            info_success = await info.async_request(zeroconf, 3000)

            if not info_success:
                return

            if "WiserHeat" in name:
                if state_change == ServiceStateChange.Added:
                    info_success = await info.async_request(zeroconf, 3000)

                    if not info_success:
                        return

                if info:
                    addresses = [
                        "%s:%d" % (addr, cast(int, info.port))
                        for addr in info.parsed_addresses()
                    ]
                    hub = _WiserDiscoveredHub(
                        ip=addresses[0].replace(":80", ""),
                        hostname=info.server.replace(".local.", ".local").lower(),
                        name=info.server.replace(".local.", ""),
                    )
                    _LOGGER.debug(
                        "Discovered Hub {} with IP Address {}".format(
                            info.server.replace(".local.", ""),
                            addresses[0].replace(":80", ""),
                        )
                    )
                    self._discovered_hubs.append(hub)

    async def discover_hub(self, min_search_time: int = 2, max_search_time: int = 10):
        """
        Call zeroconf service browser to find Wiser hubs on the local network.
        param (optional) min_search_time: min seconds to wait for responses before returning
        param (optional) max_search_time: max seconds to wait for responses before returning
        return: list of discovered hubs
        """
        timeout = 0

        self.aioZeroConf = AsyncZeroconf(ip_version=IPVersion.V4Only)
        services = ["_http._tcp.local."]
        self.aioBrowser = AsyncServiceBrowser(
            self.aioZeroConf.zeroconf,
            services,
            handlers=[self.async_on_service_state_change],
        )

        if self.mdns_timeout > 0:
            await asyncio.sleep(self.mdns_timeout)
            await self.async_close()
        return self._discovered_hubs

    async def async_close(self) -> None:
        assert self.aioZeroConf is not None
        assert self.aioBrowser is not None
        await self.aioBrowser.async_cancel()
        await self.aioZeroConf.async_close()
