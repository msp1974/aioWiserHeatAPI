"""Tests for light properties and configuration commands."""

import unittest
from unittest.mock import AsyncMock

from aioWiserHeatAPI.const import WiserLightOutputModeEnum
from aioWiserHeatAPI.light import _WiserDimmableLight, _WiserLight


class WiserLightPropertiesTest(unittest.TestCase):
    """Properties remain available on both light types."""

    def test_brightness_properties_use_the_existing_data_sources(self) -> None:
        for light_type in (_WiserLight, _WiserDimmableLight):
            with self.subTest(light_type=light_type.__name__):
                light = light_type(
                    AsyncMock(),
                    "Light/{}",
                    {"id": 12, "ScheduledPercentage": 30, "ManualLevel": 99},
                    {
                        "id": 4,
                        "ManualLevel": 40,
                        "TargetPercentage": 50,
                        "ScheduledPercentage": 98,
                    },
                    None,
                )
                self.assertEqual(light.manual_level, 40)
                self.assertEqual(light.scheduled_percentage, 30)
                self.assertEqual(light.target_percentage, 50)

    def test_missing_brightness_properties_default_to_zero(self) -> None:
        for light_type in (_WiserLight, _WiserDimmableLight):
            with self.subTest(light_type=light_type.__name__):
                light = light_type(AsyncMock(), "Light/{}", {"id": 12}, {"id": 4}, None)
                self.assertEqual(light.manual_level, 0)
                self.assertEqual(light.scheduled_percentage, 0)
                self.assertEqual(light.target_percentage, 0)


class WiserLightCommandsTest(unittest.IsolatedAsyncioTestCase):
    """Validate commands, routing, and hub-reported state handling."""

    def make_light(self, response):
        controller = AsyncMock()
        controller._send_command.return_value = response
        light = _WiserDimmableLight(
            controller,
            "Light/{}",
            {"id": 12},
            {"id": 4, "OutputMode": "Auto", "PowerOnLevel": 25},
            None,
        )
        return light, controller

    async def test_output_modes_send_canonical_values_and_update_state(self) -> None:
        for value, expected in (
            (WiserLightOutputModeEnum.auto, "Auto"),
            (WiserLightOutputModeEnum.rl_led, "RL_LED"),
            ("Auto", "Auto"),
            ("RL_LED", "RL_LED"),
            ("aUtO", "Auto"),
            ("rl_led", "RL_LED"),
        ):
            with self.subTest(value=value):
                light, controller = self.make_light({"id": 4, "OutputMode": expected})
                self.assertTrue(await light.set_output_mode(value))
                controller._send_command.assert_awaited_once_with(
                    "Light/4", {"OutputMode": expected}
                )
                self.assertEqual(light.output_mode, expected)

    async def test_invalid_output_modes_never_send_commands(self) -> None:
        for value in ("", "invalid", " Auto ", None, 1, True, []):
            with self.subTest(value=value):
                light, controller = self.make_light(False)
                with self.assertRaises(ValueError):
                    await light.set_output_mode(value)
                controller._send_command.assert_not_awaited()
                self.assertEqual(light.output_mode, "Auto")

    async def test_power_on_levels_send_to_light_endpoint_and_update_state(self) -> None:
        for level in (0, 50, 100):
            with self.subTest(level=level):
                light, controller = self.make_light({"id": 4, "PowerOnLevel": level})
                self.assertTrue(await light.set_power_on_level(level))
                controller._send_command.assert_awaited_once_with(
                    "Light/4", {"PowerOnLevel": level}
                )
                self.assertEqual(light.power_on_level, level)

    async def test_invalid_power_on_levels_never_send_commands(self) -> None:
        for level in (-1, 101, 50.5, 50.0, True, False, "50", None, float("nan")):
            with self.subTest(level=level):
                light, controller = self.make_light(False)
                with self.assertRaises(ValueError):
                    await light.set_power_on_level(level)
                controller._send_command.assert_not_awaited()
                self.assertEqual(light.power_on_level, 25)

    async def test_failed_commands_preserve_reported_state(self) -> None:
        for method, value, payload in (
            ("set_output_mode", "RL_LED", {"OutputMode": "RL_LED"}),
            ("set_power_on_level", 75, {"PowerOnLevel": 75}),
        ):
            with self.subTest(method=method):
                light, controller = self.make_light(False)
                self.assertFalse(await getattr(light, method)(value))
                controller._send_command.assert_awaited_once_with("Light/4", payload)
                self.assertEqual(light.output_mode, "Auto")
                self.assertEqual(light.power_on_level, 25)


if __name__ == "__main__":
    unittest.main()
