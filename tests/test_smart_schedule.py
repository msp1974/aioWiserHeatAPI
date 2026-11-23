"""Regression tests for optional Smart schedule data."""

import unittest

from aioWiserHeatAPI.schedule import _WiserScheduleCollection, _WiserSmartSchedule


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


class WiserSmartScheduleViewTest(unittest.TestCase):
    def test_missing_or_null_rolling_view_is_unavailable(self):
        for data in (
            {"id": 7},
            {"id": 7, "Rolling24HView": None},
            {"id": 7, "Rolling24HView": {}},
        ):
            with self.subTest(data=data):
                schedule = _WiserSmartSchedule(data)
                self.assertEqual(schedule.rolling24h_view, {})
                self.assertIsNone(schedule.expiration_date)
                self.assertIsNone(schedule.current_state)
                self.assertEqual(schedule.commands, [])
                self.assertEqual(schedule.schedule_data, data)

    def test_populated_rolling_view_preserves_hub_values(self):
        view = {
            "expirationDate": "2026-11-24T12:00:00Z",
            "currentState": "Off",
            "commands": [{"time": "12:00", "state": "On"}],
        }
        data = {"id": 7, "Rolling24HView": view, "ExtraField": "preserved"}
        schedule = _WiserSmartSchedule(data)
        self.assertEqual(schedule.expiration_date, view["expirationDate"])
        self.assertEqual(schedule.current_state, view["currentState"])
        self.assertEqual(schedule.commands, view["commands"])
        self.assertEqual(schedule.schedule_data, data)
