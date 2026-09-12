import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from time import time


class OAuthStateError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class OAuthState:
    company: str
    nonce: str
    issued_at: int

def _sign(payload: bytes, secret: bytes) -> bytes:
    return hmac.new(secret, payload, hashlib.sha256).digest()

def create_state(
    *,
    company: str,
    secret: bytes,
) -> str:
    data = {
        "company": company,
        "nonce": secrets.token_urlsafe(24),
        "issued_at": int(time()),
    }

    payload = json.dumps(
        data,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()

    signature = _sign(payload, secret)

    return ".".join(
        (
            base64.urlsafe_b64encode(payload).decode().rstrip("="),
            base64.urlsafe_b64encode(signature).decode().rstrip("="),
        )
    )

def validate_state(
    state: str,
    *,
    secret: bytes,
    max_age: int = 600,
) -> OAuthState:
    try:
        payload_part, signature_part = state.split(".", 1)

        payload = base64.urlsafe_b64decode(
            payload_part + "=" * (-len(payload_part) % 4)
        )
        signature = base64.urlsafe_b64decode(
            signature_part + "=" * (-len(signature_part) % 4)
        )
    except (ValueError, TypeError):
        raise OAuthStateError("Invalid OAuth state.") from None

    expected = _sign(payload, secret)

    if not hmac.compare_digest(signature, expected):
        raise OAuthStateError("Invalid OAuth state signature.")

    data = json.loads(payload)

    issued_at = int(data["issued_at"])

    if int(time()) - issued_at > max_age:
        raise OAuthStateError("OAuth state has expired.")

    return OAuthState(
        company=data["company"],
        nonce=data["nonce"],
        issued_at=issued_at,
    )
