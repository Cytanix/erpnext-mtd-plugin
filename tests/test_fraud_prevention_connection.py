from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from erpnext_mtd.hmrc.fraud_prevention.headers import FraudPreventionDataError
from erpnext_mtd.services.fraud_prevention import resolve_client_connection


def test_resolve_client_connection() -> None:
	request = MagicMock()
	request.remote_addr = "203.0.113.10"
	request.environ = {"REMOTE_PORT": "12345"}

	settings = SimpleNamespace(
		trusted_proxies="",
		client_ip_header="X-Forwarded-For",
		client_port_header="None",
	)
	with (
		patch("frappe.request", request),
		patch("frappe.get_single", return_value=settings),
	):
		connection = resolve_client_connection()
	assert connection.public_ip == "203.0.113.10"
	assert connection.public_port == 12345
	assert connection.timestamp.tzinfo is not None


def test_resolve_client_connection_rejects_missing_ip() -> None:
	request = MagicMock()
	request.remote_addr = None
	request.environ = {"REMOTE_PORT": "12345"}

	with patch("frappe.request", request):
		with pytest.raises(FraudPreventionDataError):
			resolve_client_connection()


def test_resolve_client_connection_rejects_missing_port() -> None:
	request = MagicMock()
	request.remote_addr = "203.0.113.10"
	request.environ = {}
	settings = MagicMock()
	settings.trusted_proxies = ""

	with (
		patch("frappe.request", request),
		patch("frappe.get_single", return_value=settings),
		pytest.raises(FraudPreventionDataError),
	):
		resolve_client_connection()


@pytest.mark.parametrize("port", ["0", "-1", "65536", "abc"])
def test_resolve_client_connection_rejects_invalid_port(port: str) -> None:
	request = MagicMock()
	request.remote_addr = "203.0.113.10"
	request.environ = {"REMOTE_PORT": port}
	settings = MagicMock()
	settings.trusted_proxies = ""

	with (
		patch("frappe.request", request),
		patch("frappe.get_single", return_value=settings),
		pytest.raises(FraudPreventionDataError),
	):
		resolve_client_connection()


def test_resolve_client_connection_from_trusted_proxy() -> None:
	request = MagicMock()
	request.remote_addr = "10.10.20.10"
	request.headers = {
		"X-Forwarded-For": "203.0.113.10",
		"X-Client-Source-Port": "45678",
	}

	settings = SimpleNamespace(
		trusted_proxies="10.10.20.10",
		client_ip_header="X-Forwarded-For",
		client_port_header="X-Client-Source-Port",
	)
	with (
		patch("frappe.request", request),
		patch("frappe.get_single", return_value=settings),
	):
		connection = resolve_client_connection()

	assert connection.public_ip == "203.0.113.10"
	assert connection.public_port == 45678


def test_resolve_client_connection_ignores_headers_from_untrusted_client() -> None:
	request = MagicMock()
	request.remote_addr = "203.0.113.10"
	request.environ = {"REMOTE_PORT": "12345"}
	request.headers = {
		"X-Forwarded-For": "198.51.100.50",
		"X-Client-Source-Port": "45678",
	}

	settings = SimpleNamespace(
		trusted_proxies="10.10.20.10",
		client_ip_header="X-Forwarded-For",
		client_port_header="X-Client-Source-Port",
	)
	with (
		patch("frappe.request", request),
		patch("frappe.get_single", return_value=settings),
	):
		connection = resolve_client_connection()

	assert connection.public_ip == "203.0.113.10"
	assert connection.public_port == 12345
