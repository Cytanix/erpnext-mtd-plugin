from frappe.tests import IntegrationTestCase

from erpnext_mtd.hmrc.oauth_session import (
	consume_oauth_session,
	store_oauth_session,
)
from erpnext_mtd.hmrc.state import OAuthStateError


class IntegrationTestOAuthSession(IntegrationTestCase):
	def test_store_and_consume_session(self) -> None:
		store_oauth_session(
			nonce="test-nonce",
			company="Cytanix Ltd",
			user="test-user"
		)

		company = consume_oauth_session(
			nonce="test-nonce",
			expected_company="Cytanix Ltd",
			expected_user="test-user"
		)

		self.assertEqual(company, "Cytanix Ltd")

	def test_session_cannot_be_replayed(self) -> None:
		store_oauth_session(
			nonce="replay-test",
			company="Cytanix Ltd",
			user="test-user"
		)

		consume_oauth_session(
			nonce="replay-test",
			expected_company="Cytanix Ltd",
			expected_user="test-user"
		)

		with self.assertRaises(OAuthStateError):
			consume_oauth_session(
				nonce="replay-test",
				expected_company="Cytanix Ltd",
				expected_user="test-user"
			)

	def test_unknown_session_is_rejected(self) -> None:
		with self.assertRaises(OAuthStateError):
			consume_oauth_session(
				nonce="does-not-exist",
				expected_company="Cytanix Ltd",
				expected_user="test-user"
			)

	def test_session_cannot_be_used_for_another_company(self) -> None:
		store_oauth_session(
			nonce="wrong-company-test",
			company="Cytanix Ltd",
			user="test-user"
		)

		with self.assertRaises(OAuthStateError):
			consume_oauth_session(
				nonce="wrong-company-test",
				expected_company="Another Company",
				expected_user="test-user"
			)
	def test_session_cannot_be_used_by_another_user(self) -> None:
		store_oauth_session(
			nonce="test-nonce",
			company="Cytanix Ltd",
			user="spirit@example.com",
		)

		with self.assertRaises(OAuthStateError):
			consume_oauth_session(
				nonce="test-nonce",
				expected_company="Cytanix Ltd",
				expected_user="attacker@example.com",
			)
