import inspect

from aioWiserHeatAPI import _LOGGER

from ..const import TEXT_UNKNOWN
from ..rest_controller import _WiserRestController


class _WiserUIConfigSensor:
    """Class representing a Wiser threshold sensor for a WIser device."""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        endpoint: str,
        data: dict,
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._endpoint = endpoint
        self._data = data

    async def _send_command(self, cmd: dict):
        """
        Send control command to the UI Configuration
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        result = await self._wiser_rest_controller._send_command(
            self._endpoint.format(self.id), cmd
        )
        if result:
            self._device_type_data = result
        if result:
            _LOGGER.debug(
                "Wiser light - {} command successful".format(
                    inspect.stack()[1].function
                )
            )
            return True
        return False

    @property
    def id(self) -> str:
        """Get the id of UIConfig sensor"""
        return self._data.get("id", 0)

    @property
    def brightness(self) -> str:
        """Get the brightness of ui config sensor"""
        return self._data.get("Brightness", 0)

    @property
    def inactive_brightness(self) -> str:
        """Get the inactive brightness of ui config sensor"""
        return self._data.get("InactiveBrightness", 0)

    @property
    def activity_timeout(self) -> str:
        """Get the activity timeout of ui config sensor"""
        return self._data.get("ActivityTimeout", 0)

    @property
    def uuid(self) -> str:
        """Get the UUID of ui config sensor"""
        return self._data.get("UUID", TEXT_UNKNOWN)

    async def set_brightness(self, enabled: bool):
        if await self._send_command({"Brightness": str(enabled).lower()}):
            return True

    async def set_inactive_brightness(self, enabled: bool):
        if await self._send_command({"InactiveBrightness": str(enabled).lower()}):
            return True
