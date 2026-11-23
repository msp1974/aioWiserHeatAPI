"""Regression tests for optional Smart schedule data."""

import unittest

from aioWiserHeatAPI.schedule import _WiserScheduleCollection


class WiserSmartScheduleCollectionTest(unittest.TestCase):
    def test_missing_or_null_overview_is_empty(self):
        for smart in ({}, {"Overview": None}, {"Overview": []}):
            for data in (smart, [smart]):
                with self.subTest(data=data):
                    schedules = _WiserScheduleCollection(
                        None, {"Smart": data}, {}, {}
                    )
                    self.assertEqual(schedules.smart_schedules, [])

    def test_populated_overview_survives_null_overview(self):
        entry = {"id": 7, "Rolling24HView": {"currentState": "On"}}
        schedules = _WiserScheduleCollection(
            None,
            {"Smart": [{"Overview": None}, {"Overview": [entry]}]},
            {},
            {},
        )
        self.assertEqual(len(schedules.smart_schedules), 1)
        self.assertEqual(schedules.smart_schedules[0].id, 7)
        self.assertEqual(schedules.smart_schedules[0].current_state, "On")
