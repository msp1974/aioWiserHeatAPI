"""Smart-plug configuration, scheduling, and command routing tests."""

import unittest
from unittest.mock import AsyncMock

from aioWiserHeatAPI.const import TEXT_UNKNOWN, WiserSmartPlugLedIndicatorEnum
from aioWiserHeatAPI.smartplug import _WiserSmartPlug


def make_plug(data=None, response=False):
    controller = AsyncMock()
    controller._send_command.return_value = response
    plug = _WiserSmartPlug(
        controller, "SmartPlug/{}", {"id": 12}, {"id": 4, **(data or {})}, None
    )
    return plug, controller


class WiserSmartPlugPropertiesTest(unittest.TestCase):
    """Expose hub-reported configuration without requiring new hub fields."""

    def test_missing_optional_fields(self) -> None:
        plug, _ = make_plug()
        self.assertFalse(plug.is_led_indicator_supported)
        self.assertEqual(plug.led_indicator, TEXT_UNKNOWN)
        self.assertEqual(plug.next_scheduled_date, TEXT_UNKNOWN)
        self.assertEqual(plug.next_scheduled_end_date, TEXT_UNKNOWN)

    def test_reported_configuration_and_schedule_dates(self) -> None:
        start, end = "2026-11-11T18:00:00", "2026-11-11T19:00:00"
        plug, _ = make_plug({
            "IsLedIndicatorSupported": True,
            "LedIndicator": "ReverseWithLoad",
            "NextScheduledDate": start,
            "NextScheduledEndDate": end,
        })
        self.assertTrue(plug.is_led_indicator_supported)
        self.assertEqual(plug.led_indicator, "ReverseWithLoad")
        self.assertEqual(plug.next_scheduled_date, start)
        self.assertEqual(plug.next_scheduled_end_date, end)

    def test_explicitly_unsupported_indicator(self) -> None:
        plug, _ = make_plug({"IsLedIndicatorSupported": False})
        self.assertFalse(plug.is_led_indicator_supported)

    def test_available_modes_exclude_light_only_mode(self) -> None:
        plug, _ = make_plug()
        self.assertEqual(
            plug.available_led_indicator,
            ["ReverseWithLoad", "ConsistentWithLoad", "AlwaysOn", "AlwaysOff"],
        )


class WiserSmartPlugCommandsTest(unittest.IsolatedAsyncioTestCase):
    """Keep generic device and SmartPlug domain IDs distinct."""

    async def test_led_modes_are_canonical_and_update_state(self) -> None:
        for mode in WiserSmartPlugLedIndicatorEnum:
            for value in (mode, mode.value, mode.value.lower(), mode.value.upper()):
                with self.subTest(value=value):
                    plug, controller = make_plug(
                        {"LedIndicator": "ConsistentWithLoad"},
                        {"id": 4, "LedIndicator": mode.value},
                    )
                    self.assertTrue(await plug.set_led_indicator(value))
                    controller._send_command.assert_awaited_once_with(
                        "SmartPlug/4", {"LedIndicator": mode.value}
                    )
                    self.assertEqual(plug.led_indicator, mode.value)
                    self.assertEqual(plug.id, 12)

    async def test_invalid_modes_do_not_send(self) -> None:
        for value in ("", "invalid", "OffAfter2s", " ReverseWithLoad ", None, True, 1, []):
            with self.subTest(value=value):
                plug, controller = make_plug({"LedIndicator": "ConsistentWithLoad"})
                with self.assertRaises(ValueError):
                    await plug.set_led_indicator(value)
                controller._send_command.assert_not_awaited()
                self.assertEqual(plug.led_indicator, "ConsistentWithLoad")

    async def test_failed_led_command_preserves_reported_state(self) -> None:
        plug, controller = make_plug({"LedIndicator": "ConsistentWithLoad"})
        self.assertFalse(await plug.set_led_indicator("ReverseWithLoad"))
        controller._send_command.assert_awaited_once_with(
            "SmartPlug/4", {"LedIndicator": "ReverseWithLoad"}
        )
        self.assertEqual(plug.led_indicator, "ConsistentWithLoad")

    async def test_turn_on_and_off_use_smartplug_id(self) -> None:
        for method, state in (("turn_on", "On"), ("turn_off", "Off")):
            with self.subTest(method=method):
                plug, controller = make_plug(response={"id": 4, "OutputState": state})
                self.assertTrue(await getattr(plug, method)())
                controller._send_command.assert_awaited_once_with(
                    "SmartPlug/4", {"RequestOutput": state}
                )
                self.assertEqual(plug.output_state, state)

    async def test_device_commands_keep_generic_device_id(self) -> None:
        plug, controller = make_plug(response={"id": 12, "DeviceLockEnabled": True})
        await plug.set_device_lock_enabled(True)
        controller._send_command.assert_awaited_once_with(
            "Device/12", {"DeviceLockEnabled": True}
        )
        self.assertTrue(plug.device_lock_enabled)
        self.assertEqual(plug.device_type_id, 4)

    async def test_failed_device_command_preserves_device_data(self) -> None:
        plug, controller = make_plug()
        self.assertFalse(await plug._send_command({"DeviceLockEnabled": True}, True))
        controller._send_command.assert_awaited_once_with(
            "Device/12", {"DeviceLockEnabled": True}
        )
        self.assertFalse(plug.device_lock_enabled)
        self.assertEqual(plug.id, 12)
        self.assertEqual(plug.device_type_id, 4)


if __name__ == "__main__":
    unittest.main()
