from datetime import UTC, datetime
from urllib.parse import quote

from .models import FraudPreventionContext, Screen, WindowSize

CONNECTION_METHOD = "WEB_APP_VIA_SERVER"


class FraudPreventionDataError(ValueError):
    pass


def encode(value: str) -> str:
    return quote(value, safe="")


def format_timestamp(timestamp: datetime) -> str:
    if timestamp.tzinfo is None:
        raise FraudPreventionDataError(
            "Public IP timestamp must be timezone-aware."
        )

    return (
        timestamp.astimezone(UTC)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

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
	return (
		f"width={window_size.width}"
		f"&height={window_size.height}"
	)

def build_headers(context: FraudPreventionContext) -> dict[str, str]:
    return {
        "Gov-Client-Connection-Method": CONNECTION_METHOD,
        "Gov-Client-Browser-JS-User-Agent": encode(
            context.browser_js_user_agent
        ),
        "Gov-Client-Device-ID": context.device_id,
        "Gov-Client-Public-IP": context.public_ip,
        "Gov-Client-Public-IP-Timestamp": format_timestamp(context.public_ip_timestamp),
        "Gov-Client-Public-Port": str(context.public_port),
        "Gov-Client-Timezone": encode(context.timezone),
        "Gov-Client-Screens": format_screens(context.screens),
        "Gov-Client-Window-Size": format_window_size(context.window_size),
        "Gov-Vendor-Product-Name": encode(context.vendor_product_name),
        "Gov-Vendor-Version": f"erpnext-mtd={encode(context.vendor_version)}",
    }
