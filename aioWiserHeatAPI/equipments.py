"""Represent and manage equipment records returned by a Wiser hub."""

from typing import Literal

from .const import WISEREQUIPMENT
from .helpers.equipment import _WiserEquipment
from .rest_controller import WiserRestActionEnum, _WiserRestController

PowerNotificationName = Literal[
    "UnderPowerNotification", "OverPowerNotification"
]


class _WiserEquipments(_WiserEquipment):
    """A single equipment record, including its writable settings."""

    def __init__(
        self, wiser_rest_controller: _WiserRestController, data: dict
    ) -> None:
        super().__init__(data)
        self._wiser_rest_controller = wiser_rest_controller

    async def _set_power_notification(
        self,
        notification_name: PowerNotificationName,
        period_mins: int,
        limit: int,
        enabled: bool,
    ) -> bool:
        """Create or replace a native power notification on the hub."""
        notification = {
            "PeriodMins": period_mins,
            "Limit": limit,
            "Enabled": enabled,
        }
        await self._wiser_rest_controller._send_command(
            WISEREQUIPMENT.format(self.id),
            {notification_name: notification},
        )
        self._data[notification_name] = notification
        return True

    async def set_under_power_notification(
        self, period_mins: int, limit: int, enabled: bool = True
    ) -> bool:
        """Create or replace the native under-power notification."""
        return await self._set_power_notification(
            "UnderPowerNotification", period_mins, limit, enabled
        )

    async def set_over_power_notification(
        self, period_mins: int, limit: int, enabled: bool = True
    ) -> bool:
        """Create or replace the native over-power notification."""
        return await self._set_power_notification(
            "OverPowerNotification", period_mins, limit, enabled
        )

    async def _set_power_notification_enabled(
        self, notification_name: PowerNotificationName, enabled: bool
    ) -> bool:
        """Update an existing notification without losing its settings."""
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

    async def _delete_power_notification(
        self, notification_name: PowerNotificationName
    ) -> bool:
        """Delete a native power notification from the hub."""
        if notification_name not in self._data:
            return False

        await self._wiser_rest_controller._send_command(
            f"{WISEREQUIPMENT.format(self.id)}/{notification_name}/",
            None,
            WiserRestActionEnum.DELETE,
        )
        self._data.pop(notification_name, None)
        return True

    async def delete_under_power_notification(self) -> bool:
        """Delete the native under-power notification."""
        return await self._delete_power_notification("UnderPowerNotification")

    async def delete_over_power_notification(self) -> bool:
        """Delete the native over-power notification."""
        return await self._delete_power_notification("OverPowerNotification")


class _WiserEquipmentsCollection:
    """Collection of equipment records reported by the hub."""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        equipments_data: list[dict] | None = None,
    ) -> None:
        records = equipments_data if isinstance(equipments_data, list) else []
        self._items = [
            _WiserEquipments(wiser_rest_controller, record)
            for record in records
            if isinstance(record, dict)
        ]
        self._items_by_id = {
            item.id: item
            for item in self._items
            if isinstance(item._data.get("id"), int)
        }

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
        return self._items_by_id.get(equipment_id)

    def get_by_equipment_id(self, equipment_id: int) -> _WiserEquipments | None:
        """Return an equipment record by its equipment id."""
        return self.get_by_id(equipment_id)

    def get_by_device_id(self, device_id: int) -> _WiserEquipments | None:
        """Return the equipment record linked to a device instance."""
        return next(
            (item for item in self._items if item.device_id == device_id),
            None,
        )
