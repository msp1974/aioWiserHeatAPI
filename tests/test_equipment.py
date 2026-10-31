"""Tests for Wiser equipment data."""

import unittest

from aioWiserHeatAPI.helpers.equipment import (
    _WiserEquipment,
    _WiserEquipmentOverPowerNotificationInfo,
    _WiserEquipmentUnderPowerNotificationInfo,
)


class WiserEquipmentNotificationTest(unittest.TestCase):
    """Test equipment power notification data."""

    def test_available_control_states_returns_advertised_states(self) -> None:
        """Available control states are exposed from the equipment data."""
        states = ["selfManagement", "consumptionForceOff"]
        equipment = _WiserEquipment({"AvailableControlState": states})

        self.assertEqual(equipment.available_control_states, states)

    def test_missing_available_control_states_returns_empty_list(self) -> None:
        """Missing available control states are represented by an empty list."""
        equipment = _WiserEquipment({})

        self.assertEqual(equipment.available_control_states, [])

    def test_over_power_notification_uses_over_power_info(self) -> None:
        """Over-power data is exposed through its matching info class."""
        equipment = _WiserEquipment(
            {
                "OverPowerNotification": {
                    "PeriodMins": 5,
                    "Limit": 1000,
                    "Enabled": True,
                }
            }
        )

        notification = equipment.over_power_notification

        self.assertIsInstance(notification, _WiserEquipmentOverPowerNotificationInfo)
        self.assertIs(notification._equipment_instance, equipment)
        self.assertEqual(notification.period_mins, 5)
        self.assertEqual(notification.limit, 1000)
        self.assertTrue(notification.enabled)

    def test_over_power_notification_preserves_zero_values(self) -> None:
        """Explicit zero values are not treated as missing configuration."""
        equipment = _WiserEquipment(
            {"OverPowerNotification": {"PeriodMins": 0, "Limit": 0}}
        )

        notification = equipment.over_power_notification

        self.assertEqual(notification.period_mins, 0)
        self.assertEqual(notification.limit, 0)

    def test_missing_over_power_values_remain_none(self) -> None:
        """Missing over-power values remain unavailable."""
        equipment = _WiserEquipment({"OverPowerNotification": {"Enabled": False}})

        notification = equipment.over_power_notification

        self.assertIsNone(notification.period_mins)
        self.assertIsNone(notification.limit)

    def test_under_power_notification_keeps_under_power_info(self) -> None:
        """Under-power data continues to use its existing info class."""
        equipment = _WiserEquipment(
            {"UnderPowerNotification": {"PeriodMins": 10, "Limit": 500}}
        )

        self.assertIsInstance(
            equipment.under_power_notification,
            _WiserEquipmentUnderPowerNotificationInfo,
        )

    def test_missing_power_notifications_return_none(self) -> None:
        """Missing notification data is represented as unavailable."""
        equipment = _WiserEquipment({})

        self.assertIsNone(equipment.under_power_notification)
        self.assertIsNone(equipment.over_power_notification)


if __name__ == "__main__":
    unittest.main()
