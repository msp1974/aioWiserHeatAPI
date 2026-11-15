"""Heating-actuator output type validation and command routing tests."""

import unittest
from unittest.mock import AsyncMock

from aioWiserHeatAPI.const import TEXT_UNKNOWN, WiserHeatingActuatorOutputTypeEnum
from aioWiserHeatAPI.heating_actuator import _WiserHeatingActuator


def make_actuator(data=None, response=False):
    controller = AsyncMock()
    controller._send_command.return_value = response
    actuator = _WiserHeatingActuator(
        controller,
        "HeatingActuator/{}",
        {"id": 12},
        {"id": 4, **(data or {})},
        None,
    )
    return actuator, controller


class WiserHeatingActuatorPropertiesTest(unittest.TestCase):
    """Preserve reported output types and missing-field defaults."""

    def test_missing_output_type(self) -> None:
        actuator, _ = make_actuator()
        self.assertEqual(actuator.output_type, TEXT_UNKNOWN)

    def test_reported_output_type(self) -> None:
        for value in ("Relay", "FilPilote", "FutureType"):
            with self.subTest(value=value):
                actuator, _ = make_actuator({"OutputType": value})
                self.assertEqual(actuator.output_type, value)

    def test_available_output_types(self) -> None:
        actuator, _ = make_actuator()
        self.assertEqual(actuator.available_output_type, ["Relay", "FilPilote"])


class WiserHeatingActuatorCommandsTest(unittest.IsolatedAsyncioTestCase):
    """Validate commands and distinguish actuator IDs from generic device IDs."""

    async def test_output_types_send_canonical_values_and_update_state(self) -> None:
        for mode in WiserHeatingActuatorOutputTypeEnum:
            for value in (mode, mode.value, mode.value.lower(), mode.value.upper()):
                with self.subTest(value=value):
                    actuator, controller = make_actuator(
                        {"OutputType": "Relay"},
                        {"id": 4, "OutputType": mode.value},
                    )
                    self.assertTrue(await actuator.set_output_type(value))
                    controller._send_command.assert_awaited_once_with(
                        "HeatingActuator/4", {"OutputType": mode.value}
                    )
                    self.assertEqual(actuator.output_type, mode.value)
                    self.assertEqual(actuator.id, 12)

    async def test_invalid_output_types_never_send(self) -> None:
        for value in ("", "invalid", " Relay ", None, True, 1, []):
            with self.subTest(value=value):
                actuator, controller = make_actuator({"OutputType": "Relay"})
                with self.assertRaises(ValueError):
                    await actuator.set_output_type(value)
                controller._send_command.assert_not_awaited()
                self.assertEqual(actuator.output_type, "Relay")

    async def test_failed_output_type_command_preserves_state(self) -> None:
        actuator, controller = make_actuator({"OutputType": "Relay"})
        self.assertFalse(await actuator.set_output_type("FilPilote"))
        controller._send_command.assert_awaited_once_with(
            "HeatingActuator/4", {"OutputType": "FilPilote"}
        )
        self.assertEqual(actuator.output_type, "Relay")
        self.assertEqual(actuator.device_type_id, 4)

    async def test_device_commands_use_generic_device_id(self) -> None:
        actuator, controller = make_actuator(
            {"OutputType": "Relay"}, {"id": 12, "DeviceLockEnabled": True}
        )
        await actuator.set_device_lock_enabled(True)
        controller._send_command.assert_awaited_once_with(
            "Device/12", {"DeviceLockEnabled": True}
        )
        self.assertTrue(actuator.device_lock_enabled)
        self.assertEqual(actuator.output_type, "Relay")
        self.assertEqual(actuator.device_type_id, 4)

    async def test_failed_device_commands_preserve_state(self) -> None:
        actuator, controller = make_actuator({"OutputType": "Relay"})
        self.assertFalse(
            await actuator._send_command({"DeviceLockEnabled": True}, True)
        )
        controller._send_command.assert_awaited_once_with(
            "Device/12", {"DeviceLockEnabled": True}
        )
        self.assertFalse(actuator.device_lock_enabled)
        self.assertEqual(actuator.id, 12)
        self.assertEqual(actuator.output_type, "Relay")


if __name__ == "__main__":
    unittest.main()
