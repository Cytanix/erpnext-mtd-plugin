# Copyright (c) 2026, Cytanix Ltd and contributors
# For license information, please see license.txt

# import frappe
from datetime import UTC, datetime

from frappe.model.document import Document

from erpnext_mtd.hmrc.oauth import OAuthToken


class HMRCAuthorisation(Document):
	def apply_token(self, token: OAuthToken) -> None:
		self.access_token = token.access_token
		self.refresh_token = token.refresh_token
		self.token_type = token.token_type
		self.scope = token.scope or ""
		self.issued_at = token.issued_at

		if token.expires_at is not None:
			self.expires_at = token.expires_at

		self.last_refreshed_at = datetime.now(UTC)
		self.status = "Authorised"
		self.last_error = ""
