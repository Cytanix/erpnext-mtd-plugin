import secrets
from typing import cast

import frappe
from frappe.utils import get_url

from erpnext_mtd.erpnext_mtd.doctype.hmrc_settings.hmrc_settings import HMRCSettings
from erpnext_mtd.hmrc.config import HMRCEnvironment
from erpnext_mtd.hmrc.oauth import build_authorization_url
from erpnext_mtd.hmrc.oauth_session import store_oauth_session
from erpnext_mtd.hmrc.state import create_state, validate_state


@frappe.whitelist()
def connect_to_hmrc(company: str) -> str:
    settings = cast(HMRCSettings, frappe.get_single("HMRC Settings"))
    if not settings.enabled:
        frappe.throw("HMRC integration is not enabled. Please enable it in HMRC Settings.")

    secret = frappe.local.conf.encryption_key.encode()

    state = create_state(company=company, secret=secret)
    state_data = validate_state(state=state, secret=secret)

    store_oauth_session(nonce=state_data.nonce, company=company)

    environment = HMRCEnvironment(settings.environment)

    redirect_uri = get_url(
        "/api/method/erpnext_mtd.api.oauth.hmrc_callback"
        )

    return build_authorization_url(
        environment,
        client_id=settings.client_id,
        redirect_uri=redirect_uri,
        scopes=("read:vat", "write:vat"),
        state=state,
    )
