import inspect

from . import _LOGGER
from .const import (
    TEXT_UNKNOWN,
    WISERAUTOMATION,
    WISERHUBAUTOMATION,
    WISERSYSTEM,
)
from .rest_controller import WiserRestActionEnum, _WiserRestController


class _WiserAutomation:
    def __init__(
        self, wiser_rest_controller: _WiserRestController, automation_data: dict
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._automation_data = automation_data
        self._details = {}
        self._details_loaded = False

    async def _send_command(self, cmd: dict) -> bool:
        """
        Send system control command to Wiser Hub
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        result = await self._wiser_rest_controller._send_command(WISERSYSTEM, cmd)
        if result:
            _LOGGER.debug(
                "Wiser hub - %s command successful", format(inspect.stack()[1].function)
            )
            return True
        return False

    @property
    def id(self) -> int:
        return self._automation_data.get("id", 0)

    @property
    def name(self) -> str:
        return self._automation_data.get("Name", TEXT_UNKNOWN)

    @property
    def enabled(self) -> bool:
        return self._automation_data.get("Enabled", False)

    async def trigger(self):
        """Activate automation"""
        return await self._send_command({"TriggerAutomation": self.id})

    @property
    def notification_enabled(self) -> bool:
        return self._automation_data.get("EnableNotification", False)

    async def get_details(self, refresh: bool = False) -> dict:
        """Return the automation triggers, actions and time constraints."""
        if refresh or not self._details_loaded:
            details = await self._wiser_rest_controller.get_hub_data(
                f"{WISERHUBAUTOMATION}{self.id}",
                False,
            )
            self._details = details if isinstance(details, dict) else {}
            self._details_loaded = True
        return self._details.copy()

    async def enable_notification(self):
        """Activate automation"""
        return await self._send_command({"EnableNotification": self.id})

    async def set_notification_enabled(self, enabled: bool) -> bool:
        """Enable or disable notifications for this automation."""
        await self._wiser_rest_controller._send_command(
            f"{WISERAUTOMATION.format(self.id)}/EnableNotification",
            enabled,
        )
        self._automation_data["EnableNotification"] = enabled
        return True

    async def set_enabled(self, enabled: bool) -> bool:
        """Enable or disable this automation."""
        await self._wiser_rest_controller._send_command(
            f"{WISERAUTOMATION.format(self.id)}/Enabled",
            enabled,
        )
        self._automation_data["Enabled"] = enabled
        return True

    async def delete(self) -> bool:
        """Delete this automation from the hub."""
        await self._wiser_rest_controller._send_command(
            WISERAUTOMATION.format(self.id),
            None,
            WiserRestActionEnum.DELETE,
        )
        return True


class _WiserAutomationCollection(object):
    def __init__(
        self, wiser_rest_controller: _WiserRestController, automations_data: dict
    ):
        self._automation_data = automations_data
        self._automations = []
        self._wiser_rest_controller = wiser_rest_controller
        self._build()

    def _build(self):
        for automation in self._automation_data:
            self._automations.append(
                _WiserAutomation(self._wiser_rest_controller, automation)
            )

    @property
    def all(self) -> list[_WiserAutomation]:
        """Return list of automations"""
        return self._automations

    @property
    def count(self) -> int:
        """Count of automations"""
        return len(self._automations)

    def get_by_id(self, automation_id: int) -> _WiserAutomation:
        try:
            return [
                automation for automation in self.all if automation.id == automation_id
            ][0]
        except IndexError:
            return None
