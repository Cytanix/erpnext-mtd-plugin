from datetime import UTC, datetime

import pytest

from erpnext_mtd.hmrc.fraud_prevention.headers import (
	FraudPreventionDataError,
	build_headers,
	encode,
	format_timestamp,
)
from erpnext_mtd.hmrc.fraud_prevention.models import (
	FraudPreventionContext,
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
