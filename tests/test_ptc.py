"""Tests for PowerTag Control commands."""

import unittest
from unittest.mock import AsyncMock

from aioWiserHeatAPI.ptc import _WiserPowerTagControl


class WiserPowerTagControlTest(unittest.IsolatedAsyncioTestCase):
    """Check PTC payloads and hub-reported state handling."""

    async def test_turn_on_and_off_set_manual_state(self) -> None:
        """Use the PTC domain ID and the field accepted by the hub."""
        for command, initial_state, requested_state in (
            ("turn_on", "Off", "On"),
            ("turn_off", "On", "Off"),
        ):
            with self.subTest(command=command):
                response = {
                    "id": 4,
                    "Mode": "Manual",
                    "ManualState": requested_state,
                    "OutputState": requested_state,
                }
                controller = AsyncMock()
                controller._send_command.return_value = response
                ptc = _WiserPowerTagControl(
                    controller,
                    "PTC/{}",
                    {"id": 12},
                    {
                        "id": 4,
                        "Mode": "Manual",
                        "ManualState": initial_state,
                        "OutputState": initial_state,
                    },
                    None,
                )

                self.assertTrue(await getattr(ptc, command)())

                controller._send_command.assert_awaited_once_with(
                    "PTC/4", {"ManualState": requested_state}
                )
                self.assertEqual(ptc.manual_state, requested_state)
                self.assertEqual(ptc.output_state, requested_state)
                self.assertEqual(ptc.is_on, requested_state == "On")

    async def test_failed_command_preserves_reported_state(self) -> None:
        """Failed requests must leave the last reported state intact."""
        for command, initial_state in (("turn_on", "Off"), ("turn_off", "On")):
            with self.subTest(command=command):
                controller = AsyncMock()
                controller._send_command.return_value = False
                ptc = _WiserPowerTagControl(
                    controller,
                    "PTC/{}",
                    {"id": 12},
                    {
                        "id": 4,
                        "ManualState": initial_state,
                        "OutputState": initial_state,
                    },
                    None,
                )

                self.assertFalse(await getattr(ptc, command)())
                self.assertEqual(ptc.manual_state, initial_state)
                self.assertEqual(ptc.output_state, initial_state)
                self.assertEqual(ptc.is_on, initial_state == "On")


if __name__ == "__main__":
    unittest.main()
