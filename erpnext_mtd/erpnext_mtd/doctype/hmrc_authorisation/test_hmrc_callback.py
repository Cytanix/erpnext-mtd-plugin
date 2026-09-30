# ERPNext MTD
#
# Copyright (C) 2026 Cytanix Ltd.
#
# SPDX-License-Identifier: GPL-3.0-only

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from erpnext_mtd.api.oauth import hmrc_callback
from erpnext_mtd.hmrc.oauth_session import consume_oauth_session, store_oauth_session
from erpnext_mtd.hmrc.state import OAuthStateError, create_state, validate_state


class IntegrationTestHMRCAuthCallback(IntegrationTestCase):
	TEST_ENCRYPTION_KEY = "test-encryption-key"

	def setUp(self) -> None:
		super().setUp()
		self.permission_patcher = patch.object(frappe, "has_permission", return_value=True)
		self.permission_patcher.start()
		self.original_encryption_key = frappe.local.conf.get("encryption_key")
		frappe.local.conf["encryption_key"] = self.TEST_ENCRYPTION_KEY
		self.original_user = frappe.session.user
		frappe.session.user = "test-user"

	def tearDown(self) -> None:
		if self.original_encryption_key is None:
			frappe.local.conf.pop("encryption_key", None)
		else:
			frappe.local.conf["encryption_key"] = self.original_encryption_key
		frappe.session.user = self.original_user
		self.permission_patcher.stop()
		super().tearDown()

	def test_callback_consumes_oauth_session(self) -> None:
		secret = self.TEST_ENCRYPTION_KEY.encode()

		state = create_state(company="Cytanix Ltd", secret=secret)
		state_data = validate_state(state=state, secret=secret)
		store_oauth_session(nonce=state_data.nonce, company=state_data.company, user="test-user")
		hmrc_callback(state=state, code="test-authorisation-code")
		with self.assertRaises(OAuthStateError):
			consume_oauth_session(
				nonce=state_data.nonce, expected_company="Cytanix Ltd", expected_user="test-user"
			)

	def test_callback_rejects_user_without_company_permission(self) -> None:
		secret = self.TEST_ENCRYPTION_KEY.encode()

		state = create_state(company="Cytanix Ltd", secret=secret)
		state_data = validate_state(state=state, secret=secret)
		store_oauth_session(
			nonce=state_data.nonce,
			company=state_data.company,
			user="test-user",
		)
		with (
			patch.object(frappe, "has_permission", return_value=False) as has_permission,
			self.assertRaises(frappe.PermissionError),
		):
			hmrc_callback(state=state, code="test-authorisation-code")

		has_permission.assert_called_once_with("Company", "write", "Cytanix Ltd")


def test_callback_handles_authorisation_denial(self) -> None:
	secret = self.TEST_ENCRYPTION_KEY.encode()

	state = create_state(company="Cytanix Ltd", secret=secret)
	state_data = validate_state(state=state, secret=secret)
	store_oauth_session(
		nonce=state_data.nonce,
		company=state_data.company,
		user="test-user",
	)

	with self.assertRaises(frappe.ValidationError) as exc:
		hmrc_callback(
			state=state,
			error="access_denied",
			error_description="The user denied access.",
		)

	self.assertIn("HMRC authorisation was not completed.", str(exc.exception))

	with self.assertRaises(OAuthStateError):
		consume_oauth_session(
			nonce=state_data.nonce,
			expected_company="Cytanix Ltd",
			expected_user="test-user",
		)


def test_callback_rejects_missing_code_and_error(self) -> None:
	secret = self.TEST_ENCRYPTION_KEY.encode()

	state = create_state(company="Cytanix Ltd", secret=secret)
	state_data = validate_state(state=state, secret=secret)
	store_oauth_session(
		nonce=state_data.nonce,
		company=state_data.company,
		user="test-user",
	)

	with self.assertRaises(frappe.ValidationError) as exc:
		hmrc_callback(state=state)

	self.assertIn(
		"HMRC did not return an authorisation code.",
		str(exc.exception),
	)


def test_callback_does_not_expose_error_description(self) -> None:
	secret = self.TEST_ENCRYPTION_KEY.encode()

	state = create_state(company="Cytanix Ltd", secret=secret)
	state_data = validate_state(state=state, secret=secret)
	store_oauth_session(
		nonce=state_data.nonce,
		company=state_data.company,
		user="test-user",
	)

	upstream_description = "<script>alert('nope')</script>"

	with self.assertRaises(frappe.ValidationError) as exc:
		hmrc_callback(
			state=state,
			error="access_denied",
			error_description=upstream_description,
		)

	self.assertNotIn(upstream_description, str(exc.exception))
