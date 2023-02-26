from aioWiserHeatAPI.const import WiserHeatingModeEnum, WiserPassiveModeEnum


class _WiserRoomAutomations:
    async def run_automations(self) -> None:
        await self.passive_mode_control()

    async def passive_mode_control(self) -> None:
        # Iterate rooms for any in pasisve mode and active heating
        passive_rooms = [room for room in self._rooms if room.is_passive_mode]
        active_heating_rooms = [
            room
            for room in self._rooms
            if (not room.is_passive_mode) and room.is_heating
        ]

        # If no passive mode rooms
        if not passive_rooms:
            return

        # Check all passive rooms are set to manual
        for room in passive_rooms:
            if (
                room.heating_mode != WiserHeatingModeEnum.manual.value
                and not room.is_boosted
            ):
                await room._send_command({"Mode": WiserHeatingModeEnum.manual.value})

        # If any active rooms are heating
        if active_heating_rooms:
            for room in passive_rooms:
                # If room is boosted do not override
                if not room.is_boosted:
                    # Set target temp to heat passive room in 0.5 increments
                    target_temp = min(
                        round((room.current_temperature + 0.5) * 2) / 2,
                        (
                            room.schedule.current_setting
                            if room.passive_mode == WiserPassiveModeEnum.schedule.value
                            and room.schedule
                            else room.passive_mode_upper_temp
                        ),
                    )
                    if target_temp != room.current_target_temperature:
                        await room.set_target_temperature(target_temp)
        else:
            # Stop any passive rooms heating by setting to min temp
            for room in passive_rooms:
                if (
                    room.current_target_temperature > room.passive_mode_lower_temp
                ) and not room.is_boosted:
                    await room.set_target_temperature(room.passive_mode_lower_temp)
