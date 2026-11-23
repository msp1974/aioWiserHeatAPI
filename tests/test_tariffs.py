"""Regression tests for optional tariff polling."""

import unittest
from unittest.mock import AsyncMock, call

from aioWiserHeatAPI.const import (
    WISERHUBDOMAIN,
    WISERHUBNETWORK,
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
from aioWiserHeatAPI.helpers.tariffs import _WiserTariffs
from aioWiserHeatAPI.wiserhub import WiserAPI


TARIFF_ENDPOINT = WISERHUBURL + WISERTARIFFS.format(
    WiserTariffTypeEnum.energytariffs.value
)


class TariffModelsTest(unittest.TestCase):
    def test_wrapped_and_direct_payloads_preserve_prices_and_intervals(self):
        energy = {
            "CurrentPrice": -0.05,
            "CurrentPrice100Multiplier": -5.0,
            "DailyAverage": 0.0,
            "DailyAverage100Multiplier": 0.0,
            "Forecast": [{
                "id": 1, "from": "2026-11-23T12:00:00Z",
                "to": "2026-11-23T13:00:00Z", "price": -0.05,
            }],
            "CurrentDay": [{"id": 2, "price": 0.0}],
        }
        for payload in (energy, {"EnergyTariff": energy}):
            with self.subTest(payload=payload):
                tariffs = _WiserTariffs(payload)
                self.assertEqual(tariffs.current_price, -0.05)
                self.assertEqual(tariffs.current_pricex100, -5.0)
                self.assertEqual(tariffs.daily_average, 0.0)
                self.assertEqual(tariffs.daily_averagex100, 0.0)
                self.assertEqual(tariffs.forecast.count, 1)
                interval = tariffs.forecast.all[0]
                self.assertEqual(interval.id, 1)
                self.assertEqual(interval.begin, energy["Forecast"][0]["from"])
                self.assertEqual(interval.end, energy["Forecast"][0]["to"])
                self.assertEqual(interval.price, -0.05)
                self.assertEqual(list(tariffs.current_day)[0].price, 0.0)
                self.assertEqual(tariffs.energy_tariff.current_price, -0.05)

    def test_missing_data_remains_unavailable(self):
        for payload in (None, {}, {"EnergyTariff": None}, {"EnergyTariff": {}}):
            with self.subTest(payload=payload):
                tariffs = _WiserTariffs(payload)
                self.assertIsNone(tariffs.current_price)
                self.assertIsNone(tariffs.current_pricex100)
                self.assertIsNone(tariffs.daily_average)
                self.assertIsNone(tariffs.daily_averagex100)
                self.assertEqual(list(tariffs.forecast), [])
                self.assertEqual(list(tariffs.current_day), [])


class TariffInitializationTest(unittest.TestCase):
    def test_tariffs_are_available_before_first_refresh(self):
        tariffs = WiserAPI("wiser.example", "secret").tariffs
        self.assertIsNone(tariffs.current_price)
        self.assertIsNone(tariffs.daily_average)
        self.assertEqual(list(tariffs.forecast), [])
        self.assertEqual(list(tariffs.current_day), [])


class TariffRefreshTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hub = WiserAPI("wiser.example", "secret")
        self.domain = {"System": {"OpenThermConnectionStatus": "Disconnected"}}
        self.tariffs = {"EnergyTariff": {"CurrentPrice": 0.25}}
        self.tariff_error = None
        self.controller = self.hub._wiser_rest_controller
        self.controller.get_hub_data = AsyncMock(side_effect=self.read)

    async def read(self, endpoint, raise_for_endpoint_error=True):
        if endpoint == TARIFF_ENDPOINT:
            if self.tariff_error is not None:
                raise self.tariff_error
            return self.tariffs
        return {
            WISERHUBDOMAIN: self.domain,
            WISERHUBNETWORK: {"Station": {}},
            WISERHUBSCHEDULES: [],
            WISERHUBSTATUS: {},
        }[endpoint]

    async def test_domain_tariffs_avoid_optional_endpoint(self):
        self.domain["Tariffs"] = self.tariffs
        await self.hub._get_hub_data()
        self.assertEqual(self.hub.raw_hub_data["Tariffs"], self.tariffs)
        self.assertNotIn(
            call(TARIFF_ENDPOINT, raise_for_endpoint_error=False),
            self.controller.get_hub_data.await_args_list,
        )

    async def test_missing_domain_tariffs_use_optional_endpoint(self):
        await self.hub._get_hub_data()
        self.assertEqual(self.hub.raw_hub_data["Tariffs"], self.tariffs)
        self.controller.get_hub_data.assert_any_await(
            TARIFF_ENDPOINT, raise_for_endpoint_error=False
        )

    async def test_unsupported_tariffs_do_not_prevent_refresh(self):
        self.tariffs = {}
        self.assertTrue(await self.hub._get_hub_data())
        self.assertEqual(self.hub.raw_hub_data["Tariffs"], {})

    async def test_optional_failure_clears_previous_tariffs(self):
        await self.hub._get_hub_data()
        for error in (WiserHubConnectionError("timeout"), WiserHubRESTError("bad JSON")):
            with self.subTest(error=type(error).__name__):
                self.tariff_error = error
                self.assertTrue(await self.hub._get_hub_data())
                self.assertEqual(self.hub.raw_hub_data["Tariffs"], {})

    async def test_authentication_error_is_not_suppressed(self):
        self.tariff_error = WiserHubAuthenticationError("unauthorized")
        with self.assertRaises(WiserHubAuthenticationError):
            await self.hub._get_hub_data()

    async def test_refresh_rebuilds_public_tariffs_and_clears_missing_data(self):
        self.domain["System"]["UnixTime"] = 0
        self.domain["Device"] = []
        self.hub._enable_automations = False
        self.controller.get_extra_config_data = AsyncMock()
        await self.hub.read_hub_data()
        self.assertIsInstance(self.hub.tariffs, _WiserTariffs)
        self.assertEqual(self.hub.tariffs.current_price, 0.25)
        self.tariffs = {"EnergyTariff": {"CurrentPrice": -0.05}}
        await self.hub.read_hub_data()
        self.assertEqual(self.hub.tariffs.current_price, -0.05)
        self.tariffs = {}
        await self.hub.read_hub_data()
        self.assertIsNone(self.hub.tariffs.current_price)
