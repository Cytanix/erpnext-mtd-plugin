# ERPNext MTD
#
# Copyright (C) 2026 Cytanix Ltd.
#
# SPDX-License-Identifier: GPL-3.0-only

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest

from erpnext_mtd.hmrc.fraud_prevention.connection import ClientConnection
from erpnext_mtd.hmrc.fraud_prevention.headers import FraudPreventionDataError
from erpnext_mtd.hmrc.fraud_prevention.models import ForwardedHop, FraudPreventionContext, MultiFactor
from erpnext_mtd.services.fraud_prevention import build_fraud_prevention_context


def client_connection() -> ClientConnection:
	return ClientConnection(
		public_ip="203.0.113.10",
		public_port=45678,
		timestamp=datetime(2026, 9, 29, tzinfo=UTC),
	)


def build_context(
	browser_data: Any,
	*,
	multi_factor: tuple[MultiFactor, ...] | None = None,
	vendor_forwarded: tuple[ForwardedHop, ...] | None = None,
	vendor_public_ip: str | None = None,
) -> FraudPreventionContext:
	with patch(
		"erpnext_mtd.services.fraud_prevention.frappe.session", SimpleNamespace(user="spirit@example.com")
	):
		return build_fraud_prevention_context(
			browser_data,
			connection=client_connection(),
			multi_factor=multi_factor,
			vendor_forwarded=vendor_forwarded,
			vendor_public_ip=vendor_public_ip,
		)


def valid_browser_data() -> dict[str, Any]:
	return {
		"browser_js_user_agent": "Mozilla/5.0 Test Browser",
		"device_id": "550e8400-e29b-41d4-a716-446655440000",
		"screens": [
			{
				"width": 1920,
				"height": 1080,
				"scaling_factor": 1.0,
				"color_depth": 24,
			}
		],
		"timezone": "Europe/London",
		"window_size": {
			"width": 1280,
			"height": 720,
		},
	}


def test_build_fraud_prevention_context() -> None:
	context = build_context(valid_browser_data())

	assert context.browser_js_user_agent == "Mozilla/5.0 Test Browser"
	assert context.device_id == "550e8400-e29b-41d4-a716-446655440000"
	assert context.public_ip == "203.0.113.10"
	assert context.public_port == 45678
	assert context.timezone == "Europe/London"
	assert context.user_id == "spirit@example.com"
	assert context.screens[0].width == 1920
	assert context.screens[0].height == 1080
	assert context.window_size.width == 1280
	assert context.window_size.height == 720


def test_build_fraud_prevention_context_preserves_optional_data() -> None:
	multi_factor = (
		MultiFactor(
			type="TOTP",
			timestamp=datetime(2026, 9, 29, 20, 0, tzinfo=UTC),
			unique_reference="factor-one",
		),
	)
	vendor_forwarded = (
		ForwardedHop(
			by="203.0.113.6",
			for_="198.51.100.0",
		),
	)

	context = build_context(
		valid_browser_data(),
		multi_factor=multi_factor,
		vendor_forwarded=vendor_forwarded,
		vendor_public_ip="203.0.113.6",
	)

	assert context.multi_factor == multi_factor
	assert context.vendor_forwarded == vendor_forwarded
	assert context.vendor_public_ip == "203.0.113.6"


def test_build_fraud_prevention_context_rejects_invalid_device_id() -> None:
	browser_data = valid_browser_data()
	browser_data["device_id"] = "definitely-not-a-uuid"

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_user_agent_control_characters() -> None:
	browser_data = valid_browser_data()
	browser_data["browser_js_user_agent"] = "Mozilla/5.0\r\nX-Evil: yes"

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_invalid_screen_dimensions() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"][0]["width"] = -1

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_invalid_scaling_factor() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"][0]["scaling_factor"] = -1.0

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_invalid_color_depth() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"][0]["color_depth"] = 0

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_invalid_window_dimensions() -> None:
	browser_data = valid_browser_data()
	browser_data["window_size"]["width"] = 0

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_invalid_timezone() -> None:
	browser_data = valid_browser_data()
	browser_data["timezone"] = "Europe/London\r\nX-Evil: yes"

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_missing_field() -> None:
	browser_data = valid_browser_data()
	del browser_data["device_id"]

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_empty_screens() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"] = []

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_invalid_screen() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"] = ["definitely a monitor"]

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_missing_screen_field() -> None:
	browser_data = valid_browser_data()
	del browser_data["screens"][0]["width"]

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_invalid_window_size() -> None:
	browser_data = valid_browser_data()
	browser_data["window_size"] = "WE LIKE TO PARTY"

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_missing_window_size_field() -> None:
	browser_data = valid_browser_data()
	del browser_data["window_size"]["width"]

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_excessive_screen_dimensions() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"][0]["width"] = 1_000_000

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_excessive_window_dimensions() -> None:
	browser_data = valid_browser_data()
	browser_data["window_size"]["width"] = 1_000_000

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_excessive_scaling_factor() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"][0]["scaling_factor"] = 1_000_000.0

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_excessive_color_depth() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"][0]["color_depth"] = 1_000_000

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)


def test_build_fraud_prevention_context_rejects_excessive_screens() -> None:
	browser_data = valid_browser_data()
	browser_data["screens"] *= 100

	with pytest.raises(FraudPreventionDataError):
		build_context(browser_data)
