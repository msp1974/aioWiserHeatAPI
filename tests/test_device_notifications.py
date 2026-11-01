"""Tests for native device notification controls."""

import unittest
from unittest.mock import AsyncMock

from aioWiserHeatAPI.binary_sensor import _WiserBinarySensor
from aioWiserHeatAPI.smokealarm import _WiserSmokeAlarm


class WiserDeviceNotificationCommandTest(unittest.IsolatedAsyncioTestCase):
    """Test notification commands for supported devices."""

    async def test_binary_sensor_notification_command(self) -> None:
        controller = AsyncMock()
        sensor = _WiserBinarySensor(
            controller,
            "BinarySensor/{}",
            {"id": 8, "Name": "Patio door"},
            {"id": 3, "Type": "WindowDoor", "EnableNotification": False},
        )

        self.assertTrue(await sensor.set_notification_enabled(True))
        controller._send_command.assert_awaited_once_with(
            "BinarySensor/3", {"EnableNotification": True}
        )
        self.assertTrue(sensor.enable_notification)

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
            "SmokeAlarmDevice/11", {"EnableNotification": False}
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
