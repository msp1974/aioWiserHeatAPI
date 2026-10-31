"""Support for Wiser equipment records."""

from .const import WISEREQUIPMENT
from .helpers.equipment import _WiserEquipment
from .rest_controller import _WiserRestController


class _WiserEquipments(_WiserEquipment):
    """Equipment data and commands for one equipment record."""

    def __init__(
        self, wiser_rest_controller: _WiserRestController, data: dict
    ) -> None:
        super().__init__(data)
        self._wiser_rest_controller = wiser_rest_controller

    async def _set_power_notification_enabled(
        self, notification_name: str, enabled: bool
    ) -> bool:
        notification = self._data.get(notification_name)
        if not isinstance(notification, dict):
            return False

        updated_notification = {
            key: notification[key]
            for key in ("PeriodMins", "Limit")
            if key in notification
        }
        updated_notification["Enabled"] = enabled
        await self._wiser_rest_controller._send_command(
            WISEREQUIPMENT.format(self.id),
            {notification_name: updated_notification},
        )
        notification["Enabled"] = enabled
        return True

    async def set_under_power_notification_enabled(self, enabled: bool) -> bool:
        """Enable or disable the under-power notification."""
        return await self._set_power_notification_enabled(
            "UnderPowerNotification", enabled
        )

    async def set_over_power_notification_enabled(self, enabled: bool) -> bool:
        """Enable or disable the over-power notification."""
        return await self._set_power_notification_enabled(
            "OverPowerNotification", enabled
        )


class _WiserEquipmentsCollection:
    """Collection of equipment records reported by the hub."""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        equipments_data: list[dict] | None = None,
    ) -> None:
        self._wiser_rest_controller = wiser_rest_controller
        self._items = [
            _WiserEquipments(wiser_rest_controller, data)
            for data in equipments_data or []
        ]

    @property
    def all(self) -> list[_WiserEquipments]:
        """Return all equipment records."""
        return list(self._items)

    @property
    def count(self) -> int:
        """Return the number of equipment records."""
        return len(self._items)

    def get_by_id(self, equipment_id: int) -> _WiserEquipments | None:
        """Return an equipment record by its id."""
        return next((item for item in self._items if item.id == equipment_id), None)

    def get_by_equipment_id(self, equipment_id: int) -> _WiserEquipments | None:
        """Return an equipment record by its equipment id."""
        return self.get_by_id(equipment_id)
