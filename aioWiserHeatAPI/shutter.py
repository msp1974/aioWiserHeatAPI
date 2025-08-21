import inspect

from . import _LOGGER
from .const import (
    TEXT_UNKNOWN,
    WISERDEVICE,
    WiserDeviceModeEnum,
    WiserShutterAwayActionEnum,
)
from .helpers.device import _WiserElectricalDevice


class _WiserLiftMovementRange(object):
    """Data structure for min/max output range"""

    def __init__(self, shutter_instance, data: dict):
        self._shutter_instance = shutter_instance
        self._data = data

    @property
    def open_time(self) -> int:
        """Get open time value"""
        if self._data:
            return self._data.get("LiftOpenTime")
        return None

    async def set_open_time(self, time: int):
        """Set open time"""
        return await self._shutter_instance._send_command(
            {"LiftOpenTime": time, "LiftCloseTime": self.close_time}
        )

    @property
    def close_time(self) -> int:
        """Get close time value"""
        if self._data:
            return self._data.get("LiftCloseTime")
        return None

    async def set_close_time(self, time: int):
        """Set close time"""
        return await self._shutter_instance._send_command(
            {"LiftOpenTime": self.open_time, "LiftCloseTime": time}
        )

    @property
    def tilt_time(self) -> int:
        """Get tilt time value"""
        if self._data:
            return self._data.get("TiltTime")
        return None

    async def set_tilt_time(self, time: int):
        """Set tilt time"""
        return await self._shutter_instance._send_command({"TiltTime": time})

    @property
    def tilt_angle_closed(self) -> int:
        """Get tilt time value"""
        if self._data:
            return self._data.get("TiltAngleClosed", 0)
        return None

    async def set_tilt_angle_closed(self, angle: int):
        """Set tilt angle closed"""
        return await self._shutter_instance._send_command(
            {"TiltAngleClosed": angle}
        )

    @property
    def tilt_angle_open(self) -> int:
        """Get tilt angle open"""
        if self._data:
            return self._data.get("TiltAngleOpen", 0)
        return None

    async def set_tilt_angle_open(self, angle: int):
        """Set tilt angle open"""
        return await self._shutter_instance._send_command(
            {"TiltAngleOpen": angle}
        )

    @property
    def tilt_enabled(self) -> bool:
        """Get tilt enabled"""
        if self._data:
            return self._data.get("TiltEnabled")
        return None

    async def set_tilt_enabled(self, en: bool):
        """Set tilt enable"""
        return await self._shutter_instance._send_command({"TiltEnabled": en})


class _WiserShutter(_WiserElectricalDevice):
    """Class representing a Wiser Shutter device"""

    async def _send_command(self, cmd: dict, device_level: bool = False):
        """
        Send control command to the smart plug
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
                self._endpoint.format(self.shutter_id), cmd
            )
            if result:
                self._device_type_data = result
        if result:
            _LOGGER.debug(
                "Wiser shutter - {} command successful".format(
                    inspect.stack()[1].function
                )
            )
            return True
        return False

    @property
    def available_away_mode_actions(self):
        return [action.value for action in WiserShutterAwayActionEnum]

    @property
    def control_source(self) -> str:
        """Get the current control source of the shutter"""
        return self._device_type_data.get("ControlSource", TEXT_UNKNOWN)

    @property
    def current_lift(self) -> bool:
        """Get amount shutter is open"""
        return self._device_type_data.get("CurrentLift", 0)

    @property
    def current_tilt(self) -> int:
        """Get current tilt of shutter"""
        return self._device_type_data.get("CurrentTilt", 0)

    @property
    def drive_config(self) -> _WiserLiftMovementRange:
        """Get open and close time drive config"""
        return _WiserLiftMovementRange(
            self, self._device_type_data.get("DriveConfig")
        )

    @property
    def is_lift_position_supported(self) -> bool:
        """Get if the shutter is open"""
        return self._device_type_data.get("IsLiftPositionSupported", False)

    @property
    def is_tilt_supported(self) -> bool:
        """Get if the shutter is open"""
        return self._device_type_data.get("IsTiltSupported", False)

    @property
    def is_open(self) -> bool:
        """Get if the shutter is open"""
        return (
            True
            if self._device_type_data.get("CurrentLift", 0) == 100
            else False
        )

    @property
    def is_closed(self) -> bool:
        """Get if the shutter is closed"""
        return (
            True
            if self._device_type_data.get("CurrentLift", 0) == 0
            else False
        )

    @property
    def is_closing(self) -> bool:
        """Get if shutter is moving-opening"""
        return (
            True
            if self._device_type_data.get("LiftMovement", TEXT_UNKNOWN)
            == "Closing"
            else False
        )

    @property
    def is_opening(self) -> bool:
        """Get if shutter is moving-opening"""
        return (
            True
            if self._device_type_data.get("LiftMovement", TEXT_UNKNOWN)
            == "Opening"
            else False
        )

    @property
    def is_stopped(self) -> bool:
        """Get if shutter is not moving"""
        return (
            True
            if self._device_type_data.get("LiftMovement", TEXT_UNKNOWN)
            == "Stopped"
            else False
        )

    @property
    def is_moving(self) -> bool:
        """Get if shutter is moving"""
        return (
            True
            if self._device_type_data.get("LiftMovement", TEXT_UNKNOWN)
            != "Stopped"
            else False
        )

    @property
    def lift_movement(self) -> str:
        """Get if shutter is moving"""
        return self._device_type_data.get("LiftMovement", TEXT_UNKNOWN)

    @property
    def manual_lift(self) -> int:
        """Get shutter manual lift value"""
        return self._device_type_data.get("ManualLift", 0)

    @property
    def manual_tilt(self) -> int:
        """Get shutter manual tilt value"""
        return self._device_type_data.get("ManualTilt", 0)

    @property
    def scheduled_lift(self) -> str:
        """Get the current scheduled lift of the shutter"""
        return self._device_type_data.get("ScheduledLift", TEXT_UNKNOWN)

    @property
    def shutter_id(self) -> int:
        """Get id of shutter"""
        return self._device_type_data.get("id", 0)

    @property
    def target_lift(self) -> int:
        """Get target position of shutter"""
        return self._device_type_data.get("TargetLift", 0)

    @property
    def tilt_movement(self) -> str:
        """Get if tilt shutter is moving"""
        return self._device_type_data.get("TiltMovement", TEXT_UNKNOWN)

    @property
    def target_tilt(self) -> int:
        """Get target tilt of shutter"""
        return self._device_type_data.get("TargetTilt", 0)

    @property
    def respect_summer_comfort(self) -> bool:
        """Get if the shutter respect summer comfort"""
        return self._device_type_data.get("RespectSummerComfort", False)

    async def set_respect_summer_comfort(self, en: bool):
        """Set respect summer comfort"""
        if await self._send_command({"RespectSummerComfort": en}):
            return True

    #Added by LGO Seasonal comfort
    @property
    def respect_seasonal_comfort(self) -> bool:
        """Get if the shutter respect seasonal comfort""" 
        return self._device_type_data.get("RespectSeasonalComfort", False)

    async def set_respect_seasonal_comfort(self, en: bool):
        """Set respect summer comfort"""
        if await self._send_command({"RespectSeasonalComfort": en}):
            return True

    @property
    def seasonal_target_lift(self) -> int:
        """Get seasonal target lift of shutter"""
        return self._device_type_data.get("SeasonalTargetLift", 0)

    async def set_seasonal_target_lift(self, lift: int):
        if await self._send_command({"SeasonalTargetLift": lift}):
            self._seasonal_target_lift = lift
            return True

    @property
    def facade(self) -> str:
        """Get facade of shutter"""
        return self._device_type_data.get("Facade", TEXT_UNKNOWN)

    @property
    def room_with_temperature_sensor (self) -> int:
        """Get the index of the temperature sensor of the room for shutter"""
        return self._device_type_data.get("RoomWithTemperatureSensor", 0)

    @property
    def use_average_temperature (self) -> bool:
        """Get use average temperature of shutter"""
        return self._device_type_data.get("UseAverageTemperature", False)

    @property
    def seasonal_derogation_utc_timestamp (self) -> int:
        """Get derogation timestamp of shutter"""
        return self._device_type_data.get("SeasonalDerogationUtcTimestamp", False)

    @property
    def covering_type (self) -> str:
        """Get the covering type Door?"""
        return self._device_type_data.get("CoveringType", TEXT_UNKNOWN)

    #End Added by LGO Seasonal comfort

    @property
    def summer_comfort_lift(self) -> int:
        """Get the shutter summer comfort lift"""
        return self._device_type_data.get("SummerComfortLift")

    async def set_summer_comfort_lift(self, lift: int):
        if await self._send_command({"SummerComfortLift": lift}):
            self._summer_comfort_lift = lift
            return True

    @property
    def summer_comfort_tilt(self) -> int:
        """Get the shutter summer comfort tilt"""
        return self._device_type_data.get("SummerComfortTilt")

    async def set_summer_comfort_tilt(self, tilt: int):
        if await self._send_command({"SummerComfortTilt": tilt}):
            self._summer_comfort_tilt = tilt
            return True

    async def open(self, percentage: int = 100):
        """Fully open shutter"""
        if percentage >= 0 and percentage <= 100:
            return await self._send_command(
                {
                    "RequestAction": {
                        "Action": "LiftTo",
                        "Percentage": percentage,
                    }
                }
            )
        else:
            raise ValueError(
                "Shutter open percentage must be between 0 and 100"
            )

    async def close(self):
        """Fully close shutter"""
        return await self._send_command(
            {"RequestAction": {"Action": "LiftTo", "Percentage": 0}}
        )

    async def stop(self):
        """Stop shutter during movement"""
        return await self._send_command({"RequestAction": {"Action": "Stop"}})

    async def open_tilt(self, percentage: int = 100):
        """Open tilt shutter to percentage"""
        if percentage >= 0 and percentage <= 100:
            return await self._send_command(
                {
                    "RequestAction": {
                        "Action": "TiltTo",
                        "Percentage": percentage,
                    }
                }
            )
        else:
            raise ValueError(
                "Shutter tilt percentage must be between 0 and 100"
            )

    async def close_tilt(self):
        """Fully close tilt shutter"""
        return await self._send_command(
            {"RequestAction": {"Action": "TiltTo", "Percentage": 0}}
        )

    async def stop_tilt(self):
        """Stop tilt shutter during movement"""
        return await self._send_command(
            {"RequestAction": {"Action": "StopTilt"}}
        )


class _WiserShutterCollection(object):
    """Class holding all wiser heating actuators"""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserShutter]:
        return list(self._items)

    @property
    def available_modes(self) -> list[str]:
        return [mode.value for mode in WiserDeviceModeEnum]

    @property
    def count(self) -> int:
        return len(self.all)

    def get_by_id(self, shutter_id: int) -> _WiserShutter:
        """
        Gets a Shutter object from the Shutters device id
        param id: device id of shutter
        return: _WiserShutter object
        """
        try:
            return [
                shutter for shutter in self.all if shutter.id == shutter_id
            ][0]
        except IndexError:
            return None

    def get_by_shutter_id(self, shutter_id: int) -> _WiserShutter:
        """
        Gets a Shutter object from the Shutters id
        param id: id of shutter
        return: _WiserShutter object
        """
        try:
            return [
                shutter
                for shutter in self.all
                if shutter.shutter_id == shutter_id
            ][0]
        except IndexError:
            return None

    def get_by_room_id(self, room_id: int) -> list[_WiserShutter]:
        """
        Gets a Shutter object from the Shutters room_id
        param id: room_id of shutter
        return: list of _WiserShutter objects
        """
        return [shutter for shutter in self.all if shutter.room_id == room_id]
