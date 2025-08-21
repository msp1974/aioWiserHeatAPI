import inspect
from aioWiserHeatAPI import _LOGGER

from .helpers.battery import _WiserBattery
from .helpers.device import _WiserDevice
from .helpers.temp import _WiserTemperatureFunctions as tf
from .const import (WISERSMOKEALARM,WISERDEVICE)

class _WiserSmokeAlarm(_WiserDevice):
    """Class representing a Wiser Smoke Alarm device"""

    async def _send_command(self, cmd: dict, device_level: bool = False):
        """
        Send control command to the smoke alarm device.
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        if device_level:
            result = await self._wiser_rest_controller._send_command(
                WISERDEVICE.format(self.id), cmd
            )
            if result:
                self._data = result
        else:
            result = await self._wiser_rest_controller._send_command(
                self._endpoint.format(self.device_type_id), cmd
            )
            if result:
                self._device_type_data = result
        if result:
            _LOGGER.debug(
                "Wiser light - {} command successful".format(
                    inspect.stack()[1].function
                )
            )
            return True
        return False

    @property
    def smokealarm_id(self) -> int:
        """Return room_id."""
        return self._data.get("id")

    @property
    def alarm_sound_level(self) -> int:
        """Get the alarm sound level"""
        return self._device_type_data.get("AlarmSoundLevel")

    @property
    def alarm_sound_mode(self) -> int:
        """Get the alarm sound mode"""
        return self._device_type_data.get("AlarmSoundMode")

    @property
    def battery(self):
        """Get battery information for smoke alarm"""
        return _WiserBattery(self._data)

    @property
    def current_temperature(self) -> float:
        """Get the current temperature measured by the smoke alarm"""
        return tf._from_wiser_temp(
            self._device_type_data.get("MeasuredTemperature"), "current"
        )

    @property
    def led_brightness(self) -> int:
        """Get the led brightness"""
        return self._device_type_data.get("LEDBrightness")

    @property
    def life_time(self) -> int:
        """Get the life time"""
        return self._device_type_data.get("LifeTime")

    @property
    def hush_duration(self) -> int:
        """Get the hush duration"""
        return self._device_type_data.get("HushDuration")

    @property
    def smoke_alarm(self) -> bool:
        """Get if smoke alarm active"""
        return self._device_type_data.get("SmokeAlarm", False)

    @property
    def heat_alarm(self) -> bool:
        """Get if heat alarm active"""
        return self._device_type_data.get("HeatAlarm", False)

    @property
    def tamper_alarm(self) -> bool:
        """Get if tamper alarm active"""
        return self._device_type_data.get("Tamper", False)

    @property
    def fault_warning(self) -> bool:
        """Get if fault warning active"""
        return self._device_type_data.get("FaultWarning", False)

    @property
    def ac_mains(self) -> bool:
        """Get if on ac mains power"""
        return self._device_type_data.get("ACMains", False)

    @property
    def test_mode(self) -> bool:
        """Get if in test mode"""
        return self._device_type_data.get("TestMode", False)

    @property
    def battery_defect(self) -> bool:
        """Get if battery defect detected"""
        return self._device_type_data.get("BatteryDefect", False)

    @property
    def remote_alarm(self) -> bool:
        """Get if remote alarm active"""
        return self._device_type_data.get("RemoteAlarm", False)

    @property
    def hush_mode(self) -> bool:
        """Get if in hush mode"""
        return self._device_type_data.get("HushMode", False)

    @property
    def report_count(self) -> int:
        """Get the report count"""
        return self._device_type_data.get("ReportCount")

    @property
    def enable_notification(self) -> bool:
        """Get if notifications active"""
        return self._device_type_data.get("EnableNotification", False)

    async def set_enable_notification(self, enabled: bool):
        """ set enable notification on smoka alarm"""      
        if await self._send_command({"EnableNotification": str(enabled).lower()}):
            self._enable_notification = enabled


    @property
    def notification_enabled(self) -> bool:
        """Get if notifications active"""
        return self._device_type_data.get("EnableNotification", False)
    @property
    def supervision_notify(self) -> bool:
        """Get if supervision notify active"""
        return self._device_type_data.get("SupervisionNotify", False)

    @property
    def restore_notify(self) -> bool:
        """Get if restore notify active"""
        return self._device_type_data.get("RestoreNotify", False)


class _WiserSmokeAlarmCollection(object):
    """Class holding all wiser smoke alarms"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserSmokeAlarm]:
        return list(self._items)

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, smokealarm_id: int) -> _WiserSmokeAlarm:
        """
        Gets a smoke alarm object from the smoke alarms id
        param id: id of smoke alarm
        return: _WiserSmokeAlarm object
        """
        try:
            return [
                smokealarm for smokealarm in self.all if smokealarm.id == smokealarm_id
            ][0]
        except IndexError:
            return None
