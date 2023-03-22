from aioWiserHeatAPI.const import WiserHeatingModeEnum


class _WiserRoomAutomations:
    async def run_automations(self) -> bool:
        return await self.passive_mode_control()

    async def passive_mode_control(self) -> bool:
        hub_updated: bool = False

        # Iterate rooms for any in pasisve mode and active heating
        passive_rooms = [room for room in self._rooms if room.is_passive_mode]
        active_heating_rooms = [
            room
            for room in self._rooms
            if (not room.is_passive_mode) and room.percentage_demand > 0
        ]

        # If no passive mode rooms
        if not passive_rooms:
            return hub_updated

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
                                + room.passive_temperature_increment
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
                        await room.set_target_temperature(target_temp)
                        hub_updated = True
        else:
            # Stop any passive rooms heating by setting to min temp
            for room in passive_rooms:
                if (
                    room.current_target_temperature > room.passive_mode_lower_temp
                ) and not room.is_boosted:
                    await room.set_target_temperature(room.passive_mode_lower_temp)
                    hub_updated = True

        return hub_updated
