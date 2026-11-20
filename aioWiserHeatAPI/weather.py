"""
Handles weather data
"""

import inspect

from .. import _LOGGER
from ..const import TEXT_UNKNOWN, WISERWEATHER
from .temp import _WiserTemperatureFunctions as tf


class _WiserWeather:
    def __init__(
        self, weather_data: dict
    ):
        self._weather_data = weather_data          

    @property
    def temperature(self) -> float:
        """Get the outside temperature """
        if  self._weather_data.get("Temperature") is not None:
            return tf._from_wiser_temp(
            self._weather_data.get("Temperature", None), "current"
            )
               
    @property
    def next_day_2pm_temperature(self) -> float:
        """Get the outside temperature next day at 2PM"""
        return tf._from_wiser_temp(
            self._weather_data.get("NextDay2pmTemperature", None), "current"
        )
