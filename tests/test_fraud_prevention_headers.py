from datetime import UTC, datetime

import pytest

from erpnext_mtd.hmrc.fraud_prevention.headers import (
    FraudPreventionDataError,
    encode,
    format_timestamp,
)


def test_encode() -> None:
    assert encode("Europe/London") == "Europe%2FLondon"


def test_format_timestamp() -> None:
    timestamp = datetime(
        2026, 9, 26, 1, 23, 45, 123000, tzinfo=UTC
    )

    assert format_timestamp(timestamp) == "2026-09-26T01:23:45.123Z"


def test_format_timestamp_rejects_naive_datetime() -> None:
    timestamp = datetime(2026, 9, 26, 1, 23, 45)

    with pytest.raises(FraudPreventionDataError):
        format_timestamp(timestamp)

def test_encode_vendor_product_name() -> None:
    assert encode("ERPNext MTD") == "ERPNext%20MTD"
