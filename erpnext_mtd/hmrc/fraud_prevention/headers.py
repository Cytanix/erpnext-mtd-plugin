# ERPNext MTD
#
# Copyright (C) 2026 Cytanix Ltd.
#
# SPDX-License-Identifier: GPL-3.0-only

from datetime import UTC, datetime
from urllib.parse import quote

from .models import (
	ForwardedHop,
	FraudPreventionContext,
	MultiFactor,
	Screen,
	WindowSize,
)

CONNECTION_METHOD = "WEB_APP_VIA_SERVER"


class FraudPreventionDataError(ValueError):
	pass


def encode(value: str) -> str:
	return quote(value, safe="")


def format_timestamp(timestamp: datetime) -> str:
	if timestamp.tzinfo is None:
		raise FraudPreventionDataError("Public IP timestamp must be timezone-aware.")

	return timestamp.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def format_screens(screens: tuple[Screen, ...]) -> str:
	return ",".join(
		(
			f"width={screen.width}"
			f"&height={screen.height}"
			f"&scaling-factor={screen.scaling_factor}"
			f"&colour-depth={screen.color_depth}"
		)
		for screen in screens
	)


def format_window_size(window_size: WindowSize) -> str:
	return f"width={window_size.width}&height={window_size.height}"


def format_multi_factor(multi_factor: tuple[MultiFactor, ...]) -> str:
	return ",".join(
		(
			f"type={encode(mf.type)}"
			f"&timestamp={encode(format_timestamp(mf.timestamp))}"
			f"&unique-reference={encode(mf.unique_reference)}"
		)
		for mf in multi_factor
	)


def format_vendor_forwarded(hops: tuple[ForwardedHop, ...]) -> str:
	return ",".join(f"by={encode(hop.by)}&for={encode(hop.for_)}" for hop in hops)


def build_headers(context: FraudPreventionContext) -> dict[str, str]:
	headers = {
		"Gov-Client-Connection-Method": CONNECTION_METHOD,
		"Gov-Client-Browser-JS-User-Agent": context.browser_js_user_agent,
		"Gov-Client-Device-ID": context.device_id,
		"Gov-Client-Public-IP": context.public_ip,
		"Gov-Client-Public-IP-Timestamp": format_timestamp(context.public_ip_timestamp),
		"Gov-Client-Public-Port": str(context.public_port),
		"Gov-Client-Timezone": context.timezone,
		"Gov-Client-Screens": format_screens(context.screens),
		"Gov-Client-Window-Size": format_window_size(context.window_size),
		"Gov-Vendor-Product-Name": encode(context.vendor_product_name),
		"Gov-Vendor-Version": f"erpnext-mtd={encode(context.vendor_version)}",
	}
	if context.multi_factor:
		headers["Gov-Client-Multi-Factor"] = format_multi_factor(context.multi_factor)

	if context.vendor_forwarded:
		headers["Gov-Vendor-Forwarded"] = format_vendor_forwarded(context.vendor_forwarded)

	if context.vendor_license_ids:
		headers["Gov-Vendor-License-IDs"] = context.vendor_license_ids

	if context.vendor_public_ip:
		headers["Gov-Vendor-Public-IP"] = context.vendor_public_ip

	return headers
