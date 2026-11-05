"""Tests for Wiser REST command payloads."""

import unittest
from unittest.mock import patch

from aioWiserHeatAPI.rest_controller import (
    WiserRestActionEnum,
    _WiserConnectionInfo,
    _WiserRestController,
)


class _FakeResponse:
    ok = True
    status = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def read(self):
        return b"false"


class _FakeSession:
    last_request = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    def request(self, method, url, **kwargs):
        type(self).last_request = (method, url, kwargs)
        return _FakeResponse()


class WiserRestPayloadTest(unittest.IsolatedAsyncioTestCase):
    """Test serialization of scalar JSON command payloads."""

    async def test_false_boolean_is_sent_as_json(self) -> None:
        connection_info = _WiserConnectionInfo()
        connection_info.host = "wiser.example.com"
        connection_info.port = 80
        connection_info.secret = "secret"
        controller = _WiserRestController(
            wiser_connection_info=connection_info
        )

        with patch(
            "aioWiserHeatAPI.rest_controller.aiohttp.ClientSession",
            _FakeSession,
        ):
            result = await controller._execute_request(
                WiserRestActionEnum.PATCH,
                "http://{}:{}/data/v2/domain/Automation/12/Enabled",
                False,
            )

        self.assertFalse(result)
        _, _, kwargs = _FakeSession.last_request
        self.assertEqual(kwargs["data"], b"false")
        self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")


if __name__ == "__main__":
    unittest.main()
