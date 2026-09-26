import json

import frappe

from .state import OAuthStateError

OAUTH_SESSION_TTL = 600
CACHE_PREFIX = "erpnext_mtd:oauth_state"

def _key(nonce: str) -> str:
    return f"{CACHE_PREFIX}:{nonce}"

def store_oauth_session(
        *,
        nonce: str,
        company: str,
        user: str,
        ttl: int = OAUTH_SESSION_TTL,
) -> None:
    if not frappe.cache:
        raise OAuthStateError("Cache is not available")
    value = json.dumps({
        "company": company,
        "user": user,
    })
    frappe.cache.set_value(
        _key(nonce),
        value,
        expires_in_sec=ttl
    )

def consume_oauth_session(
        *,
        nonce: str,
        expected_company: str,
        expected_user: str,
) -> str:
    if not frappe.cache:
        raise OAuthStateError("Cache is not available")

    key = _key(nonce)
    value = frappe.cache.get_value(key)

    if value is None:
        raise OAuthStateError("OAuth state is unknown, expired or has already been used")

    data = json.loads(value)
    company = data.get("company")
    user = data.get("user")

    if company is None:
        raise OAuthStateError("OAuth state is unknown, expired or has already been used")

    if user is None:
        raise OAuthStateError("OAuth state is unknown, expired or has already been used")

    if company != expected_company:
        raise OAuthStateError("OAuth state does not match the expected company")

    if user != expected_user:
        raise OAuthStateError("OAuth state does not match the expected user")

    frappe.cache.delete_value(key)
    return company
