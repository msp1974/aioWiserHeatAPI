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
from aioWiserHeatAPI.wiserhub import WiserAPI


TARIFF_ENDPOINT = WISERHUBURL + WISERTARIFFS.format(
    WiserTariffTypeEnum.energytariffs.value
)


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
