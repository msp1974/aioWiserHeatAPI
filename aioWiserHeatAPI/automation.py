import inspect

from . import _LOGGER
from .const import TEXT_UNKNOWN, WISERSYSTEM
from .rest_controller import _WiserRestController


class _WiserAutomation:
    def __init__(
        self, wiser_rest_controller: _WiserRestController, automation_data: dict
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._automation_data = automation_data

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

    async def enable_notification(self):
        """Activate automation"""
        return await self._send_command({"EnableNotification": self.id})


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
