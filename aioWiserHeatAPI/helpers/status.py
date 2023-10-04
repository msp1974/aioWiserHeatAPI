from datetime import datetime, timedelta

from ..const import TEXT_UNKNOWN


class WiserStatus:
    """Class to hold status object"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def uptime(self):
        """Get uptime of hub"""
        sec = timedelta(seconds=int(self._data.get("uptime", 0)))
        d = datetime(1, 1, 1) + sec
        return f"{d.day-1}d {d.hour:02d}:{d.minute:02d}:{d.second:02d}"

    @property
    def free_heap(self):
        """Get memory free heap"""
        return self._data.get("freeHeap", 0)

    @property
    def lowest_free_heap(self):
        """Get lowest memory free heap"""
        return self._data.get("lowestFreeHeap", 0)

    @property
    def last_reset_reason(self):
        """Get last reset reason"""
        return self._data.get("lastResetReason", TEXT_UNKNOWN)

    @property
    def task_usage_enabled(self):
        """Get of task usage enabled"""
        return self._data.get("taskUsageEnabled", False)
