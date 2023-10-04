import logging

from ..rest_controller import _WiserRestController
from ..const import WiserHeatingModeEnum
from ..heating import _WiserHeatingChannelCollection

_LOGGER = logging.getLogger(__name__)


class _WiserHeatingChannelAutomations:
    def __init__(
        self,
        rest_controller: _WiserRestController,
        heating_channels: _WiserHeatingChannelCollection,
    ):
        self._wiser_rest_controller = rest_controller
        self._heating_channels = heating_channels.all
        self._rooms = heating_channels._rooms.all

    async def run_automations(self) -> bool:
        return await self.passive_mode_control()

    async def passive_mode_control(self) -> bool:
        hub_updated: bool = False

        # iterate each heating channel
        for heating_channel in self._heating_channels:
            passive_rooms = [
                room
                for room in self._rooms
                if room.is_passive_mode
                and room.id in heating_channel.room_ids
                and room.current_temperature  # added to prevent error if trv offline
            ]

            # If no passive mode rooms
            if not passive_rooms:
                _LOGGER.debug("No passive rooms exist")
                continue

            active_heating_rooms = [
                room
                for room in self._rooms
                if room.id in heating_channel.room_ids
                and (not room.is_passive_mode)
                and room.percentage_demand > 0
            ]

            _LOGGER.debug(
                f"Heating Channel {heating_channel.id}, Passive Rooms {[room.name for room in passive_rooms]}, Active Rooms {[room.name for room in active_heating_rooms]}"
            )

            # If any active rooms are heating
            if active_heating_rooms:
                for room in passive_rooms:
                    # If room is boosted do not override
                    if not room.is_boosted:
                        # Set target temp to heat passive room in increments of passive_temperature_increment (default 0.5)
                        target_temp = min(
                            round(
                                (
                                    room.current_temperature
                                    + self._wiser_rest_controller._api_parameters.passive_mode_increment
                                )
                                * 2
                            )
                            / 2,
                            (
                                room.schedule.current_setting
                                if room.mode == WiserHeatingModeEnum.auto.value
                                and room.schedule
                                else room.passive_mode_upper_temp
                            ),
                        )
                        if target_temp != room.current_target_temperature:
                            _LOGGER.debug(
                                f"Setting {room.name} to {target_temp}C caused by active rooms on heating channel {heating_channel.id}"
                            )
                            await room.set_target_temperature(target_temp)
                            hub_updated = True
            else:
                # Stop any passive rooms heating by setting to min temp
                for room in passive_rooms:
                    if (
                        room.current_target_temperature > room.passive_mode_lower_temp
                    ) and not room.is_boosted:
                        _LOGGER.debug(
                            f"Setting {room.name} to {room.passive_mode_lower_temp}C caused by no active rooms on heating channel {heating_channel.id}"
                        )
                        await room.set_target_temperature(room.passive_mode_lower_temp)
                        hub_updated = True

        return hub_updated
