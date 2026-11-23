"""
Handles weather data
"""

from ..const import TEMP_ERROR


class _WiserWeather:
    def __init__(self, weather_data: dict):
        self._weather_data = weather_data

    def _get_temperature(self, key: str) -> float | None:
        """Convert weather readings without applying indoor temperature limits."""
        temperature = self._weather_data.get(key)
        if temperature is None or abs(temperature) >= TEMP_ERROR:
            return None
        return round(temperature / 10, 1)

    @property
    def temperature(self) -> float | None:
        """Get the outside temperature."""
        return self._get_temperature("Temperature")

    @property
    def next_day_2pm_temperature(self) -> float | None:
        """Get the outside temperature next day at 2PM"""
        return self._get_temperature("NextDay2pmTemperature")
