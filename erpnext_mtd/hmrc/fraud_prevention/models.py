from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Screen:
    width: int
    height: int
    scaling_factor: float
    color_depth: int


@dataclass(frozen=True, slots=True)
class WindowSize:
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class FraudPreventionContext:
    browser_js_user_agent: str
    device_id: str
    public_ip: str
    public_ip_timestamp: datetime
    public_port: int
    screens: tuple[Screen, ...]
    timezone: str
    user_id: str
    window_size: WindowSize

    vendor_product_name: str
    vendor_version: str

    multi_factor: str | None = None
    vendor_forwarded: str | None = None
    vendor_license_ids: str | None = None
    vendor_public_ip: str | None = None
