# ERPNext MTD
#
# Copyright (C) 2026 Cytanix Ltd.
#
# SPDX-License-Identifier: GPL-3.0-only

from datetime import UTC, datetime

import pytest

from erpnext_mtd.hmrc.fraud_prevention.headers import (
	FraudPreventionDataError,
	build_headers,
	encode,
	format_multi_factor,
	format_timestamp,
	format_vendor_forwarded,
)
from erpnext_mtd.hmrc.fraud_prevention.models import (
	ForwardedHop,
	FraudPreventionContext,
	MultiFactor,
	Screen,
	WindowSize,
)


def test_encode() -> None:
	assert encode("Europe/London") == "Europe%2FLondon"


def test_format_timestamp() -> None:
	timestamp = datetime(2026, 9, 26, 1, 23, 45, 123000, tzinfo=UTC)

	assert format_timestamp(timestamp) == "2026-09-26T01:23:45.123Z"


def test_format_timestamp_rejects_naive_datetime() -> None:
	timestamp = datetime(2026, 9, 26, 1, 23, 45)

	with pytest.raises(FraudPreventionDataError):
		format_timestamp(timestamp)


def test_encode_vendor_product_name() -> None:
	assert encode("ERPNext MTD") == "ERPNext%20MTD"


def test_build_headers_preserves_browser_user_agent_and_timezone() -> None:
	user_agent = (
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
		"(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
	)

	context = FraudPreventionContext(
		browser_js_user_agent=user_agent,
		device_id="550e8400-e29b-41d4-a716-446655440000",
		public_ip="203.0.113.10",
		public_ip_timestamp=datetime(2026, 9, 29, tzinfo=UTC),
		public_port=45678,
		screens=(
			Screen(
				width=1920,
				height=1080,
				scaling_factor=1.0,
				color_depth=24,
			),
		),
		timezone="UTC+01:00",
		user_id="spirit@example.com",
		window_size=WindowSize(width=1280, height=720),
		vendor_product_name="ERPNext MTD",
		vendor_version="0.0.1",
	)

	headers = build_headers(context)

	assert headers["Gov-Client-Browser-JS-User-Agent"] == user_agent
	assert headers["Gov-Client-Timezone"] == "UTC+01:00"
	assert "Gov-Client-Multi-Factor" not in headers
	assert "Gov-Vendor-Forwarded" not in headers
	assert "Gov-Vendor-License-IDs" not in headers
	assert "Gov-Vendor-Public-IP" not in headers


def test_format_multi_factor() -> None:
	multi_factor = (
		MultiFactor(
			type="AUTH_CODE",
			timestamp=datetime(2026, 9, 29, 21, 38, 0, tzinfo=UTC),
			unique_reference="factor-one",
		),
		MultiFactor(
			type="TOTP",
			timestamp=datetime(2026, 9, 29, 21, 38, 0, tzinfo=UTC),
			unique_reference="factor-two",
		),
	)

	assert format_multi_factor(multi_factor) == (
		"type=AUTH_CODE&timestamp=2026-09-29T21%3A38%3A00.000Z&unique-reference=factor-one,"
		"type=TOTP&timestamp=2026-09-29T21%3A38%3A00.000Z&unique-reference=factor-two"
	)


def test_format_vendor_forwarded() -> None:
	hops = (
		ForwardedHop(
			by="2001:0db8:85a3:0000:0000:8a2e:0370:7334",
			for_="198.51.100.0",
		),
		ForwardedHop(
			by="203.0.113.6",
			for_="2001:0db8:85a3:0000:0000:8a2e:0370:7334",
		),
		ForwardedHop(
			by="176.30.57.118",
			for_="203.0.113.6",
		),
	)

	assert format_vendor_forwarded(hops) == (
		"by=2001%3A0db8%3A85a3%3A0000%3A0000%3A8a2e%3A0370%3A7334&for=198.51.100.0,"
		"by=203.0.113.6&for=2001%3A0db8%3A85a3%3A0000%3A0000%3A8a2e%3A0370%3A7334,"
		"by=176.30.57.118&for=203.0.113.6"
	)


def test_build_headers_includes_optional_headers() -> None:
	context = FraudPreventionContext(
		browser_js_user_agent="Mozilla/5.0",
		device_id="550e8400-e29b-41d4-a716-446655440000",
		public_ip="198.51.100.0",
		public_ip_timestamp=datetime(2026, 9, 29, 20, 0, tzinfo=UTC),
		public_port=45678,
		screens=(
			Screen(
				width=1920,
				height=1080,
				scaling_factor=1.0,
				color_depth=24,
			),
		),
		timezone="UTC+01:00",
		user_id="spirit@example.com",
		window_size=WindowSize(width=1280, height=720),
		vendor_product_name="ERPNext MTD",
		vendor_version="0.0.1",
		multi_factor=(
			MultiFactor(
				type="TOTP",
				timestamp=datetime(2026, 9, 29, 19, 30, tzinfo=UTC),
				unique_reference="factor-one",
			),
		),
		vendor_forwarded=(
			ForwardedHop(
				by="203.0.113.6",
				for_="198.51.100.0",
			),
		),
		vendor_license_ids="erpnext-mtd=deadbeef",
		vendor_public_ip="203.0.113.6",
	)

	headers = build_headers(context)

	assert headers["Gov-Client-Multi-Factor"] == (
		"type=TOTP&timestamp=2026-09-29T19%3A30%3A00.000Z&unique-reference=factor-one"
	)
	assert headers["Gov-Vendor-Forwarded"] == "by=203.0.113.6&for=198.51.100.0"
	assert headers["Gov-Vendor-License-IDs"] == "erpnext-mtd=deadbeef"
	assert headers["Gov-Vendor-Public-IP"] == "203.0.113.6"
