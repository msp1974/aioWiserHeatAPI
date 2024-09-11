"""Helper functions for time."""

from datetime import datetime

from aioWiserHeatAPI.const import WEEKDAYS, WEEKENDS


def _format_output(suntimes: list[str]) -> dict[str, str]:
    output = {}
    today = datetime.today().weekday()
    days = WEEKDAYS + WEEKENDS
    for i, suntime in enumerate(suntimes[(6 - today) :]):
        # Add day of week and formatted time
        if i < 7:
            output.update({days[(i) % 7]: _format_time(suntime)})
    return output


def _format_time(time: int) -> str:
    """Format int time format to str."""
    time = str(time).rjust(4, "0")
    return time[:2] + ":" + time[2:]


def sunrise_times(times) -> dict[str, str]:
    """Return dict of sunrise times."""
    return _format_output(times)


def sunset_times(times) -> dict[str, str]:
    """Return dict of sunset times."""
    return _format_output(times)
