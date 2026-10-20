"""Tests for Wiser schedule values."""

import unittest

from aioWiserHeatAPI.const import TEMP_OFF, TEXT_HEATING
from aioWiserHeatAPI.schedule import _WiserScheduleNext


class WiserScheduleNextTest(unittest.TestCase):
    """Test conversion of the next scheduled setting."""

    def test_heating_off_period_returns_off_temperature(self) -> None:
        """A null heating setpoint represents an off schedule period."""
        next_entry = _WiserScheduleNext(TEXT_HEATING, {"DegreesC": None})

        self.assertEqual(next_entry.setting, TEMP_OFF)

    def test_heating_period_returns_temperature(self) -> None:
        """A normal heating setpoint is converted to degrees Celsius."""
        next_entry = _WiserScheduleNext(TEXT_HEATING, {"DegreesC": 195})

        self.assertEqual(next_entry.setting, 19.5)

    def test_invalid_high_heating_period_remains_unavailable(self) -> None:
        """An invalid high setpoint must not be mistaken for off."""
        next_entry = _WiserScheduleNext(TEXT_HEATING, {"DegreesC": 2000})

        self.assertIsNone(next_entry.setting)


if __name__ == "__main__":
    unittest.main()
