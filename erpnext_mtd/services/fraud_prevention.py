from datetime import UTC, datetime
from ipaddress import ip_address, ip_network
from typing import Any

import frappe
from erpnext import __version__

from erpnext_mtd.hmrc.fraud_prevention.connection import ClientConnection
from erpnext_mtd.hmrc.fraud_prevention.headers import FraudPreventionDataError
from erpnext_mtd.hmrc.fraud_prevention.models import (
	FraudPreventionContext,
	Screen,
	WindowSize,
)


def resolve_client_connection() -> ClientConnection:
	request = frappe.request
	remote_addr = request.remote_addr

	if not remote_addr:
		raise FraudPreventionDataError("Client IP is unavailable.")

	settings = frappe.get_single("HMRC Settings")

	if _is_trusted_proxy(remote_addr, settings.trusted_proxies):
		public_ip = _get_proxy_header(settings.client_ip_header, "Client IP")
		public_port = _get_proxy_header(settings.client_port_header, "Client Port")

		public_ip = public_ip.split(",", 1)[0].strip()
	else:
		public_ip = remote_addr
		public_port = request.environ.get("REMOTE_PORT")

	try:
		ip_address(public_ip)
	except ValueError as exc:
		raise FraudPreventionDataError(f"Client IP is invalid.: {public_ip}") from exc

	if public_port is None:
		raise FraudPreventionDataError("Client port is unavailable.")

	try:
		port = int(public_port)
	except (TypeError, ValueError) as exc:
		raise FraudPreventionDataError(f"Client port is not in the valid range (1-65535): {public_port}") from exc
	if not 1 <= port <= 65535:
		raise FraudPreventionDataError(f"Client port is not in the valid range (1-65535): {public_port}")

	return ClientConnection(
		public_ip=public_ip,
		public_port=port,
		timestamp=datetime.now(tz=UTC),
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


def build_fraud_prevention_context(
	browser_data: dict[str, Any],
	*,
	connection: ClientConnection,
	vendor_public_ip: str | None = None,
) -> FraudPreventionContext:
	screens = tuple(
		Screen(
			width=screen["width"],
			height=screen["height"],
			scaling_factor=screen["scaling_factor"],
			color_depth=screen["color_depth"],
		)
		for screen in browser_data["screens"]
	)
	window = browser_data["window_size"]
	return FraudPreventionContext(
		browser_js_user_agent=browser_data["browser_js_user_agent"],
		device_id=browser_data["device_id"],
		public_ip=connection.public_ip,
		public_ip_timestamp=connection.timestamp,
		public_port=connection.public_port,
		screens=screens,
		timezone=browser_data["timezone"],
		user_id=frappe.session.user,
		window_size=WindowSize(
			width=window["width"],
			height=window["height"],
		),
		vendor_product_name="ERPNext MTD",
		vendor_version=_get_app_version(),
		vendor_public_ip=vendor_public_ip,
	)


def _get_app_version() -> str:
	return __version__
