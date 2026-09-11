# Copyright (c) 2026, Cytanix Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class HMRCSettings(Document):
	def validate(self):
		if not self.enabled:
			return

		if not self.environment:
			frappe.throw(_("Environment is required when HMRC integration is enabled."))

		if not self.client_id:
			frappe.throw(_("Client ID is required when HMRC integration is enabled."))

		if not self.get_password("client_secret", raise_exception=False):
			frappe.throw(_("Client Secret is required when HMRC integration is enabled."))
