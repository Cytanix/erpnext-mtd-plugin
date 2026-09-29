from datetime import UTC, datetime
from ipaddress import ip_address, ip_network
from math import isfinite
from typing import Any
from uuid import UUID

import frappe
from erpnext import __version__

from erpnext_mtd.hmrc.fraud_prevention.connection import ClientConnection
from erpnext_mtd.hmrc.fraud_prevention.headers import FraudPreventionDataError
from erpnext_mtd.hmrc.fraud_prevention.models import (
	FraudPreventionContext,
	Screen,
	WindowSize,
)

# Arbitrary upper limits to prevent unreasonable values. These limits are not based on any specific standard, but are intended to catch obviously invalid data.
_MAX_SCREEN_COUNT = 16
_MAX_DISPLAY_DIMENSION = 100_000
_MAX_SCALING_FACTOR = 100
_MAX_COLOR_DEPTH = 128


def resolve_client_connection() -> ClientConnection:
	request = frappe.request
	remote_addr = request.remote_addr

	if not remote_addr:
		raise FraudPreventionDataError("Client IP is unavailable.")

	settings = frappe.get_single("HMRC Settings")

	if _is_trusted_proxy(remote_addr, settings.trusted_proxies):
		public_ip = _get_proxy_header(settings.client_ip_header, "Client IP")
		public_port = _get_proxy_header(settings.client_port_header, "Client Port")

		public_ip = public_ip.strip()
		if "," in public_ip:
			raise FraudPreventionDataError("Client IP header must contain exactly one IP address.")
	else:
		if (settings.client_ip_header and request.headers.get(settings.client_ip_header)) or (
			settings.client_port_header and request.headers.get(settings.client_port_header)
		):
			raise FraudPreventionDataError("Proxy headers are not allowed from an untrusted client.")

		public_ip = remote_addr
		public_port = request.environ.get("REMOTE_PORT")

	try:
		ip_address(public_ip)
	except ValueError as exc:
		raise FraudPreventionDataError(f"Client IP is invalid: {public_ip}") from exc

	if public_port is None:
		raise FraudPreventionDataError("Client port is unavailable.")

	try:
		port = int(public_port)
	except (TypeError, ValueError) as exc:
		raise FraudPreventionDataError(
			f"Client port is not in the valid range (1-65535): {public_port}"
		) from exc
	if not 1 <= port <= 65535:
		raise FraudPreventionDataError(f"Client port is not in the valid range (1-65535): {public_port}")

	return ClientConnection(
		public_ip=public_ip,
		public_port=port,
		timestamp=datetime.now(tz=UTC),
	)


def build_fraud_prevention_context(
	browser_data: Any,
	*,
	connection: ClientConnection,
	vendor_public_ip: str | None = None,
) -> FraudPreventionContext:
	browser_data = _validate_browser_data(browser_data)
	screens = tuple(_parse_screen(screen) for screen in _validate_screens(browser_data["screens"]))
	window_size = _parse_window_size(browser_data["window_size"])
	browser_js_user_agent = _validate_browser_string(
		browser_data["browser_js_user_agent"],
		description="Browser JS User Agent",
		max_length=1024,
	)
	timezone = _validate_browser_string(
		browser_data["timezone"],
		description="Timezone",
		max_length=1024,
	)
	device_id = _validate_device_id(browser_data["device_id"])

	return FraudPreventionContext(
		public_ip=connection.public_ip,
		public_ip_timestamp=connection.timestamp,
		public_port=connection.public_port,
		screens=screens,
		user_id=frappe.session.user,
		vendor_product_name="ERPNext MTD",
		vendor_version=_get_app_version(),
		vendor_public_ip=vendor_public_ip,
		device_id=device_id,
		window_size=window_size,
		browser_js_user_agent=browser_js_user_agent,
		timezone=timezone,
	)


def _validate_device_id(value: Any) -> str:
	if not isinstance(value, str):
		raise FraudPreventionDataError("Device ID must be a string")

	try:
		UUID(value)
	except ValueError as exc:
		raise FraudPreventionDataError("Device ID must be a valid UUID") from exc

	return value


def _validate_browser_string(
	value: Any,
	*,
	description: str,
	max_length: int,
) -> str:
	if not isinstance(value, str):
		raise FraudPreventionDataError(f"{description} must be a string.")

	if not value:
		raise FraudPreventionDataError(f"{description} must not be empty.")

	if len(value) > max_length:
		raise FraudPreventionDataError(f"{description} must not exceed {max_length} characters.")

	if any(ord(char) < 32 or ord(char) == 127 for char in value):
		raise FraudPreventionDataError(f"{description} must not contain control characters.")

	return value


def _validate_positive_int(value: Any, *, description: str, max_value: int | None = None) -> int:
	if isinstance(value, bool) or not isinstance(value, int):
		raise FraudPreventionDataError(f"{description} must be an integer.")

	if value <= 0:
		raise FraudPreventionDataError(f"{description} must be a positive integer.")

	if max_value is not None and value > max_value:
		raise FraudPreventionDataError(f"{description} must not exceed {max_value}.")

	return value


def _validate_positive_number(value: Any, *, description: str, max_value: float | None = None) -> int | float:
	if isinstance(value, bool) or not isinstance(value, (int, float)):
		raise FraudPreventionDataError(f"{description} must be a number.")

	if not isfinite(value) or value <= 0:
		raise FraudPreventionDataError(f"{description} must be a finite number greater than zero.")

	if max_value is not None and value > max_value:
		raise FraudPreventionDataError(f"{description} must not exceed {max_value}.")

	return value


def _validate_browser_data(browser_data: Any) -> dict[str, Any]:
	if not isinstance(browser_data, dict):
		raise FraudPreventionDataError("Browser data must be a dictionary.")

	required_keys = {
		"browser_js_user_agent",
		"device_id",
		"screens",
		"timezone",
		"window_size",
	}

	missing_keys = required_keys - browser_data.keys()
	if missing_keys:
		raise FraudPreventionDataError(f"Browser data is missing required keys: {sorted(missing_keys)[0]}")

	return browser_data


def _validate_screens(screens: Any) -> list[Any]:
	if not isinstance(screens, list):
		raise FraudPreventionDataError("Screens must be a list.")

	if not screens:
		raise FraudPreventionDataError("Screens list must not be empty.")

	if len(screens) > _MAX_SCREEN_COUNT:
		raise FraudPreventionDataError(
			f"Screens list must not contain more than {_MAX_SCREEN_COUNT} screens."
		)

	return screens


def _parse_screen(value: Any) -> Screen:
	if not isinstance(value, dict):
		raise FraudPreventionDataError("Screen must be an object.")

	required_fields = {
		"width",
		"height",
		"scaling_factor",
		"color_depth",
	}

	missing_fields = required_fields - value.keys()
	if missing_fields:
		raise FraudPreventionDataError(f"Screen is missing required field: {sorted(missing_fields)[0]}.")

	return Screen(
		width=_validate_positive_int(
			value["width"],
			description="Screen width",
			max_value=_MAX_DISPLAY_DIMENSION,
		),
		height=_validate_positive_int(
			value["height"],
			description="Screen height",
			max_value=_MAX_DISPLAY_DIMENSION,
		),
		scaling_factor=_validate_positive_number(
			value["scaling_factor"],
			description="Screen scaling factor",
			max_value=_MAX_SCALING_FACTOR,
		),
		color_depth=_validate_positive_int(
			value["color_depth"],
			description="Screen color depth",
			max_value=_MAX_COLOR_DEPTH,
		),
	)


def _parse_window_size(value: Any) -> WindowSize:
	if not isinstance(value, dict):
		raise FraudPreventionDataError("Window size must be an object.")

	required_fields = {"width", "height"}
	missing_fields = required_fields - value.keys()

	if missing_fields:
		raise FraudPreventionDataError(f"Window size is missing required field: {sorted(missing_fields)[0]}.")

	return WindowSize(
		width=_validate_positive_int(
			value["width"],
			description="Window width",
			max_value=_MAX_DISPLAY_DIMENSION,
		),
		height=_validate_positive_int(
			value["height"],
			description="Window height",
			max_value=_MAX_DISPLAY_DIMENSION,
		),
	)


def _is_trusted_proxy(remote_addr: str, configured_proxies: str | None) -> bool:
	if not configured_proxies:
		return False

	try:
		address = ip_address(remote_addr)
	except ValueError as exc:
		raise FraudPreventionDataError(f"Client IP is invalid: {remote_addr}") from exc

	for value in configured_proxies.splitlines():
		value = value.strip()
		if not value:
			continue

		try:
			network = ip_network(value)
		except ValueError as exc:
			raise FraudPreventionDataError(f"Configured trusted proxy is invalid: {value}") from exc

		if address in network:
			return True

	return False


def _get_proxy_header(header_name: str | None, description: str) -> str:
	if not header_name:
		raise FraudPreventionDataError(f"{description} header is not configured.")

	value = frappe.request.headers.get(header_name)

	if not value:
		raise FraudPreventionDataError(f"{description} header is unavailable.")

	return value


def _get_app_version() -> str:
	return __version__
