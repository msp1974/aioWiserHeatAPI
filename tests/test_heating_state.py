"""Heating state and refresh regressions using the real API objects."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from aioWiserHeatAPI.const import (
    WISERHUBDOMAIN,
    WISERHUBNETWORK,
    WISERHUBOPENTHERM,
    WISERHUBOPENTHERMV2,
    WISERHUBSCHEDULES,
    WISERHUBSTATUS,
    WISERHUBURL,
    WISERTARIFFS,
    WiserTariffTypeEnum,
)
from aioWiserHeatAPI.exceptions import (
    WiserHubAuthenticationError,
    WiserHubConnectionError,
    WiserHubRESTError,
)
from aioWiserHeatAPI.helpers.automations import _WiserHeatingChannelAutomations
from aioWiserHeatAPI.helpers.opentherm import _WiserOpentherm
from aioWiserHeatAPI.rest_controller import WiserAPIParams
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.wiserhub import WiserAPI


def boiler(status="Connected", data=None, ever_connected=False):
    return _WiserOpentherm(None, data or {}, status, ever_connected)


def room(opentherm=None, **data):
    # Only the state properties are under test; no schedule or devices needed.
    result = object.__new__(_WiserRoom)
    result._data = data
    result._opentherm = opentherm
    return result


class PassiveScheduleTest(unittest.IsolatedAsyncioTestCase):
    async def test_limiter_leaves_matching_schedule_target_to_hub(self):
        for active_demand in (0, 20):
            for lower in (17, 16):
                with self.subTest(active_demand=active_demand, lower=lower):
                    limiter = room(
                        id=1,
                        DisplayedSetPoint=180,
                        CalculatedTemperature=179,
                        SetpointOrigin="FromSchedule",
                    )
                    limiter._enable_automations = True
                    limiter._name = "Lounge"
                    limiter._extra_config = {"passive_mode": True, "max": 22}
                    limiter._mode = "Auto"
                    limiter._schedule = SimpleNamespace(current_setting=17)
                    limiter.set_target_temperature = AsyncMock(return_value=True)
                    controller = SimpleNamespace(
                        _api_parameters=WiserAPIParams(
                            passive_mode_lower_temp_provider=lambda _: lower,
                            passive_mode_temperature_limiter_provider=lambda _: True,
                        )
                    )
                    limiter._wiser_rest_controller = controller
                    active_room = SimpleNamespace(
                        id=2,
                        name="Office",
                        is_passive_mode=False,
                        percentage_demand=active_demand,
                    )
                    channels = SimpleNamespace(
                        all=[SimpleNamespace(id=1, room_ids=[1, 2])],
                        _rooms=SimpleNamespace(all=[limiter, active_room]),
                    )

                    updated = await _WiserHeatingChannelAutomations(
                        controller, channels
                    ).run_automations()

                    if lower == 17:
                        self.assertFalse(updated)
                        limiter.set_target_temperature.assert_not_awaited()
                    else:
                        self.assertTrue(updated)
                        limiter.set_target_temperature.assert_awaited_once_with(16)


class HeatingStateTest(unittest.TestCase):
    def test_relay_rooms_keep_using_control_output(self):
        for status in ("On", "Off"):
            for demand in (0, 50):
                with self.subTest(status=status, demand=demand):
                    result = room(
                        boiler("Disconnected"),
                        ControlOutputState=status,
                        PercentageDemand=demand,
                    )
                    self.assertIs(result.is_heating, status == "On")

    def test_opentherm_requires_room_demand_and_ch_activity(self):
        for demand in (0, 50):
            for slave in (0, 2, 4, 8, 12):
                with self.subTest(demand=demand, slave=slave):
                    result = room(
                        boiler(data={
                            "Enabled": True,
                            "operationalData": {"SlaveStatus": slave},
                        }),
                        PercentageDemand=demand,
                        ControlOutputState="On",
                    )
                    self.assertIs(
                        result.is_heating, demand > 0 and bool(slave & 2)
                    )

    def test_missing_or_invalid_slave_status_is_unknown(self):
        for value in (None, True, False, "2", 2.0):
            with self.subTest(value=value):
                ot = boiler(data={
                    "Enabled": True,
                    "operationalData": {"SlaveStatus": value},
                })
                self.assertIsNone(ot.central_heating_active)
                self.assertIsNone(room(ot, PercentageDemand=50).is_heating)

    def test_missing_or_invalid_operational_data_is_unknown(self):
        for data in ({}, {"operationalData": None}, {"operationalData": []}):
            with self.subTest(data=data):
                self.assertIsNone(boiler(data=data).central_heating_active)

    def test_missing_or_invalid_room_demand_is_unknown(self):
        ot = boiler(data={
            "Enabled": True, "operationalData": {"SlaveStatus": 2},
        })
        invalid = (None, True, "50", -1, 101, float("nan"), float("inf"))
        for data in ({}, *({"PercentageDemand": v} for v in invalid)):
            with self.subTest(data=data):
                result = room(ot, **data)
                self.assertIsNone(result.is_calling_for_heat)
                self.assertIsNone(result.is_heating)

    def test_disconnected_or_disabled_opentherm_does_not_use_room_output(self):
        for ot in (
            boiler("Disconnected", {"Enabled": True}),
            boiler("Disconnected", ever_connected=True),
            boiler("Unknown", ever_connected=True),
            boiler(data={"Enabled": False, "operationalData": {"SlaveStatus": 2}}),
        ):
            for output in ("On", "Off"):
                with self.subTest(status=ot.connection_status, output=output):
                    result = room(
                        ot, PercentageDemand=50, ControlOutputState=output
                    )
                    self.assertIsNone(result.is_heating)


class HeatingRefreshTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hub = WiserAPI("wiser.example", "secret")
        self.domain = {
            "System": {
                "UnixTime": 0,
                "HardwareGeneration": 1,
                "OpenThermConnectionStatus": "Disconnected",
            },
            "Device": [],
            "Room": [{
                "id": 1, "Name": "Room", "Mode": "Auto",
                "PercentageDemand": 50, "ControlOutputState": "On",
            }],
            "HeatingChannel": [{"id": 1, "RoomIds": [1]}],
            "HotWater": [{"id": 2}],
        }
        self.ot_data = {"Enabled": True, "operationalData": {"SlaveStatus": 2}}
        self.ot_error = None
        self.controller = self.hub._wiser_rest_controller
        self.controller.get_hub_data = AsyncMock(side_effect=self.read)
        self.controller.get_extra_config_data = AsyncMock()

    async def read(self, endpoint, raise_for_endpoint_error=True):
        if endpoint in (WISERHUBOPENTHERM, WISERHUBOPENTHERMV2):
            if self.ot_error:
                raise self.ot_error
            return self.ot_data
        return {
            WISERHUBDOMAIN: self.domain,
            WISERHUBNETWORK: {"Station": {}},
            WISERHUBSCHEDULES: [],
            WISERHUBSTATUS: {},
            WISERHUBURL + WISERTARIFFS.format(
                WiserTariffTypeEnum.energytariffs.value
            ): {},
        }[endpoint]

    async def test_relay_hub_does_not_poll_opentherm(self):
        await self.hub.read_hub_data()
        calls = [
            call.args[0] for call in self.controller.get_hub_data.await_args_list
        ]
        self.assertNotIn(WISERHUBOPENTHERM, calls)
        self.assertNotIn(WISERHUBOPENTHERMV2, calls)
        self.assertTrue(self.hub.rooms.get_by_id(1).is_heating)

    async def test_connection_loss_and_recovery(self):
        self.domain["System"]["OpenThermConnectionStatus"] = "Connected"
        await self.hub.read_hub_data()
        self.assertTrue(self.hub.rooms.get_by_id(1).is_heating)
        self.domain["System"]["OpenThermConnectionStatus"] = "Disconnected"
        await self.hub.read_hub_data()
        self.assertIsNone(self.hub.rooms.get_by_id(1).is_heating)
        self.assertEqual(self.hub.system.opentherm.json_data, {})
        self.domain["System"]["OpenThermConnectionStatus"] = "Connected"
        await self.hub.read_hub_data()
        self.assertTrue(self.hub.rooms.get_by_id(1).is_heating)

    async def test_known_opentherm_disconnected_on_startup(self):
        self.hub.api_parameters.opentherm_ever_connected = True
        await self.hub.read_hub_data()
        self.assertIsNone(self.hub.rooms.get_by_id(1).is_heating)

    async def test_optional_endpoint_failure_clears_previous_data(self):
        self.domain["System"]["OpenThermConnectionStatus"] = "Connected"
        await self.hub.read_hub_data()
        for error in (
            WiserHubConnectionError("timeout"), WiserHubRESTError("bad JSON")
        ):
            with self.subTest(error=type(error).__name__):
                self.ot_error = error
                await self.hub.read_hub_data()
                self.assertEqual(self.hub.system.opentherm.json_data, {})
                self.assertIsNone(self.hub.rooms.get_by_id(1).is_heating)
                self.assertIsNotNone(self.hub.heating_channels)

    async def test_malformed_endpoint_response_is_unknown(self):
        self.domain["System"]["OpenThermConnectionStatus"] = "Connected"
        self.ot_data = None
        await self.hub.read_hub_data()
        self.assertIsNone(self.hub.rooms.get_by_id(1).is_heating)

    async def test_authentication_failure_is_not_suppressed(self):
        self.domain["System"]["OpenThermConnectionStatus"] = "Connected"
        self.ot_error = WiserHubAuthenticationError("unauthorized")
        with self.assertRaises(WiserHubAuthenticationError):
            await self.hub.read_hub_data()

    async def test_firmware_selects_correct_opentherm_endpoint(self):
        for generation, version, expected in (
            (1, "4.99.0", WISERHUBOPENTHERM),
            (2, "4.32.46", WISERHUBOPENTHERM),
            (2, "4.32.47", WISERHUBOPENTHERMV2),
        ):
            with self.subTest(generation=generation, version=version):
                self.domain["System"].update(
                    HardwareGeneration=generation,
                    ActiveSystemVersion=version,
                    OpenThermConnectionStatus="Connected",
                )
                self.controller.get_hub_data.reset_mock()
                await self.hub.read_hub_data()
                self.controller.get_hub_data.assert_any_await(expected, False)
