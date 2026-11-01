"""Tests for EVSE equipment-backed properties."""

import unittest
from unittest.mock import AsyncMock

from aioWiserHeatAPI.evse import _WiserEVSE


class WiserEVSEEquipmentTest(unittest.TestCase):
    """Test EVSE values sourced from its equipment record."""

    def test_available_control_states_uses_equipment_validation(self) -> None:
        """EVSE control states use the same validated equipment accessor."""
        states = ["selfManagement", "consumptionForceOff"]
        evse = _WiserEVSE(
            AsyncMock(),
            "Equipment/{}",
            {"id": 8},
            {"id": 21, "AvailableControlState": states},
        )

        result = evse.available_control_states
        result.append("invalid")

        self.assertEqual(result[:-1], states)
        self.assertEqual(states, ["selfManagement", "consumptionForceOff"])

    def test_invalid_control_states_are_not_exposed(self) -> None:
        """Malformed equipment control-state data becomes an empty list."""
        evse = _WiserEVSE(
            AsyncMock(),
            "Equipment/{}",
            {"id": 8},
            {"id": 21, "AvailableControlState": "selfManagement"},
        )

        self.assertEqual(evse.available_control_states, [])


if __name__ == "__main__":
    unittest.main()
