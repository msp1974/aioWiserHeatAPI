"""Tests for Wiser equipment collections and commands."""

import unittest
from unittest.mock import AsyncMock

from aioWiserHeatAPI.devices import _WiserDeviceCollection
from aioWiserHeatAPI.equipments import (
    _WiserEquipments,
    _WiserEquipmentsCollection,
)
from aioWiserHeatAPI.rest_controller import WiserRestActionEnum


class WiserEquipmentsCollectionTest(unittest.TestCase):
    """Test equipment collection access."""

    def test_collection_contains_domain_equipment(self) -> None:
        """The device collection exposes all domain equipment separately."""
        equipment_data = [{"id": 21, "EquipmentName": "Solar inverter"}]
        devices = _WiserDeviceCollection(
            AsyncMock(),
            {"Device": [], "Equipment": equipment_data},
            None,
        )

        self.assertEqual(devices.equipments.count, 1)
        equipment = devices.equipments.get_by_id(21)
        self.assertIsInstance(equipment, _WiserEquipments)
        self.assertEqual(equipment.equipment_name, "Solar inverter")
        self.assertEqual(devices.equipments.all, [equipment])

    def test_empty_collection_is_available(self) -> None:
        """A hub without equipment exposes an empty collection."""
        devices = _WiserDeviceCollection(AsyncMock(), {"Device": []}, None)

        self.assertEqual(devices.equipments.all, [])
        self.assertEqual(devices.equipments.count, 0)
        self.assertIsNone(devices.equipments.get_by_id(21))

    def test_get_by_equipment_id_uses_equipment_record_id(self) -> None:
        """Equipment lookup by equipment id finds the matching record."""
        collection = _WiserEquipmentsCollection(
            AsyncMock(), [{"id": 21}, {"id": 22}]
        )

        self.assertEqual(collection.get_by_equipment_id(22).id, 22)

    def test_collection_ignores_malformed_equipment_data(self) -> None:
        """Unexpected domain data cannot break collection construction."""
        collection = _WiserEquipmentsCollection(AsyncMock(), {"id": 21})

        self.assertEqual(collection.all, [])
        self.assertEqual(collection.count, 0)

    def test_collection_ignores_non_mapping_records(self) -> None:
        """Only object-shaped equipment records become equipment instances."""
        collection = _WiserEquipmentsCollection(
            AsyncMock(), [{"id": 21}, None, "invalid"]
        )

        self.assertEqual(collection.count, 1)
        self.assertEqual(collection.get_by_id(21).id, 21)

    def test_get_by_device_id_uses_application_instance_id(self) -> None:
        """Linked equipment can be resolved from its physical device id."""
        collection = _WiserEquipmentsCollection(
            AsyncMock(),
            [{"id": 21, "DeviceApplicationInstanceId": 8}],
        )

        self.assertEqual(collection.get_by_device_id(8).id, 21)


class WiserEquipmentNotificationCommandTest(unittest.IsolatedAsyncioTestCase):
    """Test equipment power notification commands."""

    async def test_set_notification_enabled_sends_command_and_updates_data(
        self,
    ) -> None:
        """A successful notification command updates local equipment data."""
        controller = AsyncMock()
        controller._send_command.return_value = {"Enabled": True}
        equipment = _WiserEquipments(
            controller,
            {
                "id": 21,
                "UnderPowerNotification": {
                    "PeriodMins": 5,
                    "Limit": 1000,
                    "Enabled": False,
                },
                "OverPowerNotification": {"Enabled": False},
            },
        )

        self.assertFalse(equipment.over_power_notification.enabled)
        result = await equipment.set_under_power_notification_enabled(True)

        self.assertTrue(result)
        controller._send_command.assert_awaited_once_with(
            "Equipment/21",
            {
                "UnderPowerNotification": {
                    "PeriodMins": 5,
                    "Limit": 1000,
                    "Enabled": True,
                }
            },
        )
        self.assertTrue(equipment.under_power_notification.enabled)

    async def test_set_notification_enabled_accepts_empty_success_response(
        self,
    ) -> None:
        """A successful command with an empty response updates local data."""
        controller = AsyncMock()
        controller._send_command.return_value = {}
        equipment = _WiserEquipments(
            controller,
            {
                "id": 21,
                "UnderPowerNotification": {
                    "PeriodMins": 5,
                    "Limit": 1000,
                    "Enabled": False,
                },
            },
        )

        result = await equipment.set_under_power_notification_enabled(True)

        self.assertTrue(result)
        self.assertTrue(equipment.under_power_notification.enabled)

    async def test_set_notification_enabled_preserves_missing_thresholds(
        self,
    ) -> None:
        """Missing notification thresholds are not replaced with zero values."""
        controller = AsyncMock()
        controller._send_command.return_value = {}
        equipment = _WiserEquipments(
            controller,
            {"id": 21, "OverPowerNotification": {"Enabled": False}},
        )

        result = await equipment.set_over_power_notification_enabled(True)

        self.assertTrue(result)
        controller._send_command.assert_awaited_once_with(
            "Equipment/21",
            {"OverPowerNotification": {"Enabled": True}},
        )
        self.assertTrue(equipment.over_power_notification.enabled)

    async def test_set_notification_enabled_returns_false_when_not_configured(
        self,
    ) -> None:
        """Missing notification configuration does not issue a command."""
        controller = AsyncMock()
        equipment = _WiserEquipments(controller, {"id": 21})

        result = await equipment.set_over_power_notification_enabled(True)

        self.assertFalse(result)
        controller._send_command.assert_not_awaited()

    async def test_create_under_power_notification(self) -> None:
        """A complete under-power notification is sent and stored locally."""
        controller = AsyncMock()
        equipment = _WiserEquipments(controller, {"id": 21})

        result = await equipment.set_under_power_notification(5, 0)

        self.assertTrue(result)
        controller._send_command.assert_awaited_once_with(
            "Equipment/21",
            {
                "UnderPowerNotification": {
                    "PeriodMins": 5,
                    "Limit": 0,
                    "Enabled": True,
                }
            },
        )
        self.assertEqual(equipment.under_power_notification.period_mins, 5)
        self.assertEqual(equipment.under_power_notification.limit, 0)
        self.assertTrue(equipment.under_power_notification.enabled)

    async def test_update_over_power_notification(self) -> None:
        """Setting a notification replaces all of its configurable values."""
        controller = AsyncMock()
        equipment = _WiserEquipments(
            controller,
            {
                "id": 21,
                "OverPowerNotification": {
                    "PeriodMins": 5,
                    "Limit": 100,
                    "Enabled": True,
                },
            },
        )

        result = await equipment.set_over_power_notification(10, 250, False)

        self.assertTrue(result)
        controller._send_command.assert_awaited_once_with(
            "Equipment/21",
            {
                "OverPowerNotification": {
                    "PeriodMins": 10,
                    "Limit": 250,
                    "Enabled": False,
                }
            },
        )
        self.assertEqual(equipment.over_power_notification.period_mins, 10)
        self.assertEqual(equipment.over_power_notification.limit, 250)
        self.assertFalse(equipment.over_power_notification.enabled)

    async def test_delete_over_power_notification(self) -> None:
        """Deletion uses the native notification endpoint and clears local data."""
        controller = AsyncMock()
        equipment = _WiserEquipments(
            controller,
            {
                "id": 21,
                "OverPowerNotification": {
                    "PeriodMins": 5,
                    "Limit": 100,
                    "Enabled": True,
                },
            },
        )

        result = await equipment.delete_over_power_notification()

        self.assertTrue(result)
        controller._send_command.assert_awaited_once_with(
            "Equipment/21/OverPowerNotification/",
            None,
            WiserRestActionEnum.DELETE,
        )
        self.assertIsNone(equipment.over_power_notification)

    async def test_delete_missing_notification_does_not_call_hub(self) -> None:
        """Deleting a notification that is not configured is a no-op."""
        controller = AsyncMock()
        equipment = _WiserEquipments(controller, {"id": 21})

        result = await equipment.delete_under_power_notification()

        self.assertFalse(result)
        controller._send_command.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
