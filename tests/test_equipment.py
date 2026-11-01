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

    def test_invalid_available_control_states_returns_empty_list(self) -> None:
        """Malformed control-state data is not exposed as an iterable string."""
        equipment = _WiserEquipment({"AvailableControlState": "selfManagement"})

        self.assertEqual(equipment.available_control_states, [])

    def test_available_control_states_returns_a_copy(self) -> None:
        """Consumers cannot mutate the source hub data through the property."""
        source = ["selfManagement"]
        equipment = _WiserEquipment({"AvailableControlState": source})

        equipment.available_control_states.append("consumptionForceOff")

        self.assertEqual(source, ["selfManagement"])

    def test_equipment_power_and_schedule_attributes(self) -> None:
        """Equipment-specific power and schedule fields use their matching keys."""
        equipment = _WiserEquipment(
            {
                "OverviewScheduleId": 12,
                "StatedPower": 3600,
                "CableStatedPower": 7400,
            }
        )

        self.assertEqual(equipment.overview_schedule_id, 12)
        self.assertEqual(equipment.stated_power, 3600)
        self.assertEqual(equipment.cable_stated_power, 7400)

    def test_missing_equipment_power_and_schedule_attributes(self) -> None:
        """Missing optional equipment attributes remain unavailable."""
        equipment = _WiserEquipment({})

        self.assertIsNone(equipment.overview_schedule_id)
        self.assertIsNone(equipment.stated_power)
        self.assertIsNone(equipment.cable_stated_power)

    def test_zero_equipment_values_are_preserved(self) -> None:
        """Explicit zero values are distinct from missing values."""
        equipment = _WiserEquipment(
            {
                "OverviewScheduleId": 0,
                "StatedPower": 0,
                "CableStatedPower": 0,
            }
        )

        self.assertEqual(equipment.overview_schedule_id, 0)
        self.assertEqual(equipment.stated_power, 0)
        self.assertEqual(equipment.cable_stated_power, 0)

    def test_missing_under_power_values_remain_none(self) -> None:
        """Missing under-power values are not invented as zero thresholds."""
        equipment = _WiserEquipment({"UnderPowerNotification": {"Enabled": False}})

        notification = equipment.under_power_notification

        self.assertIsNone(notification.period_mins)
        self.assertIsNone(notification.limit)

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
