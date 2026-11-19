"""Data models for the tariff information returned by a Wiser hub."""

from typing import Any, Dict, List, Optional


class _TariffInterval:
    """A single tariff interval."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data or {}

    @property
    def id(self) -> Optional[int]:
        return self._data.get("id")

    @property
    def begin(self) -> Optional[str]:
        """Start of the interval, as returned by the hub."""
        return self._data.get("from")

    @property
    def end(self) -> Optional[str]:
        """End of the interval, as returned by the hub."""
        return self._data.get("to")

    @property
    def price(self) -> Optional[float]:
        return self._data.get("price")


class _TariffIntervals:
    """A list of tariff intervals, such as Forecast or CurrentDay."""

    def __init__(self, data: Optional[List[Dict[str, Any]]] = None):
        self._intervals = [
            _TariffInterval(interval) for interval in (data or [])
        ]

    @property
    def all(self) -> List[_TariffInterval]:
        return list(self._intervals)

    @property
    def count(self) -> int:
        return len(self._intervals)

    def __iter__(self):
        return iter(self._intervals)

    def __len__(self) -> int:
        return len(self._intervals)


class _EnergyTariff:
    """Tariff data containing forecast, current day, and price summaries."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self._data = data or {}

    @property
    def forecast(self) -> _TariffIntervals:
        return _TariffIntervals(self._data.get("Forecast"))

    @property
    def current_day(self) -> _TariffIntervals:
        return _TariffIntervals(self._data.get("CurrentDay"))

    @property
    def daily_average(self) -> Optional[float]:
        return self._data.get("DailyAverage")

    @property
    def daily_averagex100(self) -> Optional[float]:
        return self._data.get("DailyAverage100Multiplier")

    @property
    def current_price(self) -> Optional[float]:
        return self._data.get("CurrentPrice")

    @property
    def current_pricex100(self) -> Optional[float]:
        return self._data.get("CurrentPrice100Multiplier")


class _WiserTariffs:
    """Top-level Tariffs response from the Wiser hub."""

    def __init__(self, tariff_data: Optional[Dict[str, Any]] = None):
        data = tariff_data or {}
        # Accept either the full response (containing EnergyTariff) or the
        # EnergyTariff object itself.
        self._energy_tariff_data = data.get("EnergyTariff", data)

    @property
    def energy_tariff(self) -> _EnergyTariff:
        return _EnergyTariff(self._energy_tariff_data)

    @property
    def forecast(self) -> _TariffIntervals:
        return self.energy_tariff.forecast

    @property
    def current_day(self) -> _TariffIntervals:
        return self.energy_tariff.current_day

    @property
    def daily_average(self) -> Optional[float]:
        return self.energy_tariff.daily_average

    @property
    def daily_averagex100(self) -> Optional[float]:
        return self.energy_tariff.daily_averagex100

    @property
    def current_price(self) -> Optional[float]:
        return self.energy_tariff.current_price

    @property
    def current_pricex100(self) -> Optional[float]:
        return self.energy_tariff.current_pricex100
