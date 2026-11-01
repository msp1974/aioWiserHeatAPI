"""Tests for Wiser REST protocol handling."""

import unittest
from unittest.mock import MagicMock

from aioWiserHeatAPI.exceptions import WiserHubRESTError
from aioWiserHeatAPI.rest_controller import (
    _WiserConnectionInfo,
    _WiserRestController,
)


class WiserRestControllerHTTPSTest(unittest.TestCase):
    """Test detection of hubs that require HTTPS."""

    def setUp(self) -> None:
        """Create a controller with valid connection information."""
        connection_info = _WiserConnectionInfo()
        connection_info.host = "wiser.example.com"
        connection_info.port = 8443
        connection_info.secret = "secret"
        self.controller = _WiserRestController(
            wiser_connection_info=connection_info
        )

    @staticmethod
    def _response(status: int, location: str = "") -> MagicMock:
        """Create the response fields used by error processing."""
        response = MagicMock()
        response.status = status
        response.headers = {"Location": location} if location else {}
        return response

    def test_https_redirect_enables_https(self) -> None:
        """An aiohttp-ok HTTPS redirect enables HTTPS for the retry."""
        response = self._response(
            301, "https://192.168.1.10/data/domain/"
        )
        response.ok = True

        self.assertFalse(self.controller._response_is_successful(response))
        with self.assertRaisesRegex(WiserHubRESTError, "requires HTTPS"):
            self.controller._process_nok_response(
                response, "http://wiser.example.com:8443/data/domain/", None
            )

        self.assertTrue(self.controller.use_https)

    def test_http_redirect_does_not_enable_https(self) -> None:
        """An unrelated HTTP redirect must not change the protocol."""
        response = self._response(
            301, "http://wiser.example.com:8443/login"
        )

        with self.assertRaises(WiserHubRESTError):
            self.controller._process_nok_response(
                response, "http://wiser.example.com:8443/data/domain/", None
            )

        self.assertFalse(self.controller.use_https)

    def test_https_port_error_enables_https(self) -> None:
        """The known HTTPS-port response enables HTTPS for the retry."""
        response = self._response(400)

        with self.assertRaisesRegex(WiserHubRESTError, "requires HTTPS"):
            self.controller._process_nok_response(
                response,
                "http://wiser.example.com:8443/data/domain/",
                None,
                response_body=(
                    "The plain HTTP request was sent to an HTTPS port"
                ),
            )

        self.assertTrue(self.controller.use_https)

    def test_generic_bad_request_does_not_enable_https(self) -> None:
        """An ordinary bad request must not change the protocol."""
        response = self._response(400)

        with self.assertRaises(WiserHubRESTError):
            self.controller._process_nok_response(
                response,
                "http://wiser.example.com:8443/data/domain/",
                None,
                response_body="Invalid request payload",
            )

        self.assertFalse(self.controller.use_https)


if __name__ == "__main__":
    unittest.main()
