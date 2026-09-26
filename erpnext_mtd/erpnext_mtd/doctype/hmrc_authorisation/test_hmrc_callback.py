import frappe
from frappe.tests import IntegrationTestCase

from erpnext_mtd.api.oauth import hmrc_callback
from erpnext_mtd.hmrc.oauth_session import consume_oauth_session, store_oauth_session
from erpnext_mtd.hmrc.state import OAuthStateError, create_state, validate_state

class IntegrationTestHMRCAuthCallback(IntegrationTestCase):
    TEST_ENCRYPTION_KEY = "test-encryption-key"
    def setUp(self) -> None:
        super().setUp()
        self.original_encryption_key = frappe.local.conf.get("encryption_key")
        frappe.local.conf["encryption_key"] = self.TEST_ENCRYPTION_KEY

    def tearDown(self) -> None:
        if self.original_encryption_key is None:
            frappe.local.conf.pop("encryption_key", None)
        else:
            frappe.local.conf["encryption_key"] = self.original_encryption_key
        super().tearDown()

    def test_callback_consumes_oauth_session(self) -> None:
        secret = self.TEST_ENCRYPTION_KEY.encode()

        state = create_state(company="Cytanix Ltd",secret=secret)
        state_data = validate_state(state=state, secret=secret)
        store_oauth_session(nonce=state_data.nonce, company=state_data.company, user="test-user")
        hmrc_callback(state=state, code="test-authorisation-code")
        with self.assertRaises(OAuthStateError):
            consume_oauth_session(nonce=state_data.nonce, expected_company="Cytanix Ltd", expected_user="test-user")