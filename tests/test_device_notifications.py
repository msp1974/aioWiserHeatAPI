"""Tests for native device notification controls."""

import unittest
from unittest.mock import AsyncMock

from aioWiserHeatAPI.automation import _WiserAutomation
from aioWiserHeatAPI.binary_sensor import _WiserBinarySensor
from aioWiserHeatAPI.const import WiserWindowDoorEnableNotificationEnum
from aioWiserHeatAPI.rest_controller import WiserRestActionEnum
from aioWiserHeatAPI.smokealarm import _WiserSmokeAlarm


class WiserDeviceNotificationCommandTest(unittest.IsolatedAsyncioTestCase):
    """Test notification commands for supported devices."""

    async def test_binary_sensor_notification_command(self) -> None:
        controller = AsyncMock()
        sensor = _WiserBinarySensor(
            controller,
            "BinarySensor/{}",
            {"id": 8, "Name": "Patio door"},
            {"id": 3, "Type": "WindowDoor", "EnableNotification": "None"},
        )

        self.assertFalse(sensor.notification_enabled)
        self.assertTrue(await sensor.set_notification_enabled(True))
        controller._send_command.assert_awaited_once_with(
            "BinarySensor/3", {"EnableNotification": "OnEither"}
        )
        self.assertEqual(sensor.enable_notification, "OnEither")
        self.assertTrue(sensor.notification_enabled)

    async def test_binary_sensor_notification_modes(self) -> None:
        controller = AsyncMock()
        sensor = _WiserBinarySensor(
            controller,
            "BinarySensor/{}",
            {"id": 8, "Name": "Patio door"},
            {"id": 3, "Type": "WindowDoor", "EnableNotification": "OnTrue"},
        )

        self.assertTrue(sensor.notification_enabled)
        self.assertEqual(
            sensor.available_enable_notification,
            ["OnEither", "None", "OnTrue", "OnFalse"],
        )
        self.assertTrue(
            await sensor.set_enable_notification(
                WiserWindowDoorEnableNotificationEnum.onfalse
            )
        )
        controller._send_command.assert_awaited_once_with(
            "BinarySensor/3", {"EnableNotification": "OnFalse"}
        )

    async def test_binary_sensor_rejects_unknown_notification_mode(self) -> None:
        sensor = _WiserBinarySensor(
            AsyncMock(),
            "BinarySensor/{}",
            {"id": 8},
            {"id": 3, "Type": "WindowDoor", "EnableNotification": "None"},
        )

        with self.assertRaisesRegex(ValueError, "invalid.*not a valid"):
            await sensor.set_enable_notification("invalid")

    async def test_smoke_alarm_notification_command(self) -> None:
        controller = AsyncMock()
        alarm = _WiserSmokeAlarm(
            controller,
            "SmokeAlarmDevice/{}",
            {"id": 11, "Name": "Landing alarm"},
            {"id": 4, "EnableNotification": True},
        )

        self.assertTrue(alarm.notification_supported)
        self.assertTrue(await alarm.set_notification_enabled(False))
        controller._send_command.assert_awaited_once_with(
            "SmokeAlarmDevice/4", {"EnableNotification": False}
        )
        self.assertFalse(alarm.notification_enabled)

    def test_smoke_alarm_reports_missing_notification_capability(self) -> None:
        alarm = _WiserSmokeAlarm(
            AsyncMock(),
            "SmokeAlarmDevice/{}",
            {"id": 11},
            {"id": 4},
        )

        self.assertFalse(alarm.notification_supported)

    async def test_automation_enabled_command(self) -> None:
        controller = AsyncMock()
        automation = _WiserAutomation(
            controller,
            {"id": 12, "Name": "Door left open", "Enabled": True},
        )

        self.assertTrue(await automation.set_enabled(False))
        controller._send_command.assert_awaited_once_with(
            "Automation/12/Enabled", False
        )
        self.assertFalse(automation.enabled)

    async def test_automation_enabled_accepts_empty_success_response(self) -> None:
        controller = AsyncMock()
        controller._send_command.return_value = {}
        automation = _WiserAutomation(
            controller,
            {"id": 12, "Name": "Door left open", "Enabled": False},
        )

        self.assertTrue(await automation.set_enabled(True))
        self.assertTrue(automation.enabled)

    async def test_automation_delete_command(self) -> None:
        controller = AsyncMock()
        automation = _WiserAutomation(
            controller,
            {"id": 12, "Name": "Door left open", "Enabled": True},
        )

        self.assertTrue(await automation.delete())
        controller._send_command.assert_awaited_once_with(
            "Automation/12", None, WiserRestActionEnum.DELETE
        )
