from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import frappe
from frappe.tests import IntegrationTestCase

from erpnext_mtd.api.oauth import connect_to_hmrc
from erpnext_mtd.hmrc.oauth_session import consume_oauth_session
from erpnext_mtd.hmrc.state import validate_state


class IntegrationTestConnectToHMRC(IntegrationTestCase):
	def test_connect_to_hmrc(self) -> None:
		class Settings:
			enabled = 1
			environment = "Sandbox"
			client_id = "test-client-id"

		with (
			patch.object(frappe, "get_single", return_value=Settings()),
		):
			url = connect_to_hmrc("Cytanix Ltd")

		parsed = urlparse(url)
		query = parse_qs(parsed.query)

		self.assertEqual(parsed.netloc, "test-www.tax.service.gov.uk")
		self.assertEqual(query["client_id"], ["test-client-id"])
		self.assertEqual(query["response_type"], ["code"])
		self.assertEqual(query["scope"], ["read:vat write:vat"])

		state = query["state"][0]

		state_data = validate_state(
			state,
			secret=frappe.local.conf.encryption_key.encode(),
		)

		company = consume_oauth_session(
			nonce=state_data.nonce,
			expected_company="Cytanix Ltd",
		)

		self.assertEqual(company, "Cytanix Ltd")

	def test_connect_to_hmrc_uses_production_environment(self) -> None:
		class Settings:
			enabled = 1
			environment = "Production"
			client_id = "test-client-id"

		with (
			patch.object(frappe, "get_single", return_value=Settings()),
		):
			url = connect_to_hmrc("Cytanix Ltd")

		parsed = urlparse(url)

		self.assertEqual(parsed.netloc, "www.tax.service.gov.uk")

	def test_connect_to_hmrc_generates_unique_state(self) -> None:
		class Settings:
			enabled = 1
			environment = "Sandbox"
			client_id = "test-client-id"

		with (
			patch.object(frappe, "get_single", return_value=Settings()),
		):
			first = parse_qs(
				urlparse(connect_to_hmrc("Cytanix Ltd")).query
			)["state"][0]

			second = parse_qs(
				urlparse(connect_to_hmrc("Cytanix Ltd")).query
			)["state"][0]

		self.assertNotEqual(first, second)

	def test_connect_to_hmrc_rejects_disabled_integration(self) -> None:
		class Settings:
			enabled = 0
			environment = "Sandbox"
			client_id = "test-client-id"

		with patch.object(
			frappe,
			"get_single",
			return_value=Settings(),
		):
			with self.assertRaises(frappe.ValidationError):
				connect_to_hmrc("Cytanix Ltd")

	def test_connect_to_hmrc_preserves_company_name(self) -> None:
		class Settings:
			enabled = 1
			environment = "Sandbox"
			client_id = "test-client-id"

		with (
			patch.object(frappe, "get_single", return_value=Settings()),
		):
			url = connect_to_hmrc("Cytanix R&D Ltd")

		state = parse_qs(urlparse(url).query)["state"][0]

		state_data = validate_state(
			state,
			secret=frappe.local.conf.encryption_key.encode(),
		)

		self.assertEqual(state_data.company, "Cytanix R&D Ltd")

		company = consume_oauth_session(
			nonce=state_data.nonce,
			expected_company="Cytanix R&D Ltd",
		)

		self.assertEqual(company, "Cytanix R&D Ltd")
