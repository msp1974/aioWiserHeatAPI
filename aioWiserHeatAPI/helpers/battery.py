from ..const import (
    ROOMSTAT_MIN_BATTERY_LEVEL,
    ROOMSTAT_FULL_BATTERY_LEVEL,
    TEXT_UNKNOWN,
    TRV_FULL_BATTERY_LEVEL,
    TRV_BATTERY_LEVEL_MAPPING,
)


def percentage_clip(value: int):
    return min(100, max(0, value))


class _WiserBattery(object):
    """Data structure for battery information for a Wiser device that is powered by batteries"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def level(self) -> str:
        """Get the descritpion of the battery level"""
        return self._data.get("BatteryLevel", TEXT_UNKNOWN)

    @property
    def percent(self) -> int:
        """Get the percent of battery remaining"""
        if self._data.get("ProductType") == "RoomStat" and self.voltage:
            return percentage_clip(
                round(
                    (
                        (self.voltage - ROOMSTAT_MIN_BATTERY_LEVEL)
                        / (ROOMSTAT_FULL_BATTERY_LEVEL - ROOMSTAT_MIN_BATTERY_LEVEL)
                    )
                    * 100
                )
            )
        elif self._data.get("ProductType") == "iTRV" and self.voltage:
            return (
                TRV_BATTERY_LEVEL_MAPPING.get(self.voltage, 0)
                if self.voltage < TRV_FULL_BATTERY_LEVEL
                else 100
            )
        else:
            return None

    @property
    def voltage(self) -> float:
        """Get the battery voltage"""
        return (
            self._data.get("BatteryVoltage") / 10
            if self._data.get("BatteryVoltage")
            else None
        )
