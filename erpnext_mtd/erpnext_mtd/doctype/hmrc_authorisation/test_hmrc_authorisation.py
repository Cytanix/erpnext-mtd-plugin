# Copyright (c) 2026, Cytanix Ltd and Contributors
# See license.txt

from datetime import UTC, datetime

from frappe.tests.utils import FrappeTestCase

from erpnext_mtd.erpnext_mtd.doctype.hmrc_authorisation.hmrc_authorisation import (
	HMRCAuthorisation,
)
from erpnext_mtd.hmrc.models import OAuthToken


class IntegrationTestHMRCAuthorisation(FrappeTestCase):
	def test_apply_token(self) -> None:
		issued_at = datetime(2026, 9, 12, 0, 0, tzinfo=UTC)

		doc = HMRCAuthorisation(
			{
				"doctype": "HMRC Authorisation",
				"company": "Cytanix Ltd",
			}
		)

		token = OAuthToken(
			access_token="access-token",
			token_type="bearer",
			expires_in=14_400,
			refresh_token="refresh-token",
			scope="read:vat write:vat",
			issued_at=issued_at,
		)

		doc.apply_token(token)

		self.assertEqual(doc.access_token, "access-token")
		self.assertEqual(doc.refresh_token, "refresh-token")
		self.assertEqual(doc.token_type, "bearer")
		self.assertEqual(doc.scope, "read:vat write:vat")
		self.assertEqual(doc.issued_at, issued_at)
		self.assertEqual(doc.expires_at, token.expires_at)
		self.assertEqual(doc.status, "Authorised")
		self.assertEqual(doc.last_error, "")
		self.assertIsNotNone(doc.last_refreshed_at)