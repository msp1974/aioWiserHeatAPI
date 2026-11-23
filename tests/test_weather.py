"""Tests for outdoor weather temperature conversion."""

import unittest

from aioWiserHeatAPI.const import TEMP_ERROR
from aioWiserHeatAPI.helpers.weather import _WiserWeather


class WiserWeatherTest(unittest.TestCase):
    def test_outdoor_temperatures_are_not_clamped_to_indoor_limits(self):
        for raw, expected in (
            (-405, -40.5), (-250, -25.0), (-200, -20.0),
            (-195, -19.5), (0, 0.0), (215, 21.5),
        ):
            with self.subTest(raw=raw):
                weather = _WiserWeather(
                    {"Temperature": raw, "NextDay2pmTemperature": raw}
                )
                self.assertEqual(weather.temperature, expected)
                self.assertEqual(weather.next_day_2pm_temperature, expected)

    def test_missing_temperatures_remain_unavailable(self):
        for data in ({}, {"Temperature": None, "NextDay2pmTemperature": None}):
            with self.subTest(data=data):
                weather = _WiserWeather(data)
                self.assertIsNone(weather.temperature)
                self.assertIsNone(weather.next_day_2pm_temperature)

    def test_error_temperatures_remain_unavailable(self):
        for raw in (TEMP_ERROR, -TEMP_ERROR, TEMP_ERROR + 1):
            with self.subTest(raw=raw):
                weather = _WiserWeather(
                    {"Temperature": raw, "NextDay2pmTemperature": raw}
                )
                self.assertIsNone(weather.temperature)
                self.assertIsNone(weather.next_day_2pm_temperature)
