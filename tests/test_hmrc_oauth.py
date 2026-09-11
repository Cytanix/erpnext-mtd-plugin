from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from erpnext_mtd.hmrc.config import HMRCEnvironment
from erpnext_mtd.hmrc.models import OAuthToken
from erpnext_mtd.hmrc.oauth import build_authorization_url, exchange_authorization_code, refresh_access_token


def test_build_sandbox_authorization_url() -> None:
	url = build_authorization_url(
		HMRCEnvironment.SANDBOX,
		client_id="test-client",
		redirect_uri="https://example.com/hmrc/callback",
		scopes=("read:vat", "write:vat"),
		state="test-state",
	)

	parsed = urlparse(url)
	query = parse_qs(parsed.query)

	assert parsed.scheme == "https"
	assert parsed.netloc == "test-www.tax.service.gov.uk"
	assert parsed.path == "/oauth/authorize"

	assert query["response_type"] == ["code"]
	assert query["client_id"] == ["test-client"]
	assert query["redirect_uri"] == ["https://example.com/hmrc/callback"]
	assert query["scope"] == ["read:vat write:vat"]
	assert query["state"] == ["test-state"]


def test_token_expiry() -> None:
	issued_at = datetime(2026, 9, 11, 20, 0, tzinfo=UTC)

	token = OAuthToken(
		access_token="access",
		token_type="bearer",
		expires_in=14_400,
		refresh_token="refresh",
		issued_at=issued_at,
	)

	assert token.expires_at == datetime(2026, 9, 12, 0, 0, tzinfo=UTC)

	assert not token.is_expired(now=datetime(2026, 9, 11, 23, 59, tzinfo=UTC))

	assert token.is_expired(now=datetime(2026, 9, 12, 0, 0, tzinfo=UTC))


@pytest.mark.asyncio
async def test_exchange_authorization_code() -> None:
	async def handler(request: httpx.Request) -> httpx.Response:
		body = request.content.decode()

		assert request.method == "POST"
		assert request.url.path == "/oauth/token"
		assert "grant_type=authorization_code" in body
		assert "client_id=test-client" in body
		assert "client_secret=test-secret" in body
		assert "code=test-code" in body

		return httpx.Response(
			200,
			json={
				"access_token": "access-1",
				"token_type": "bearer",
				"expires_in": 14400,
				"refresh_token": "refresh-1",
				"scope": "read:vat write:vat",
			},
		)

	token = await exchange_authorization_code(
		HMRCEnvironment.SANDBOX,
		client_id="test-client",
		client_secret="test-secret",
		code="test-code",
		redirect_uri="https://example.com/callback",
		transport=httpx.MockTransport(handler),
	)

	assert token.access_token == "access-1"
	assert token.refresh_token == "refresh-1"
	assert token.expires_in == 14400


@pytest.mark.asyncio
async def test_refresh_access_token() -> None:
	async def handler(request: httpx.Request) -> httpx.Response:
		body = request.content.decode()

		assert "grant_type=refresh_token" in body
		assert "refresh_token=refresh-old" in body

		return httpx.Response(
			200,
			json={
				"access_token": "access-2",
				"token_type": "bearer",
				"expires_in": 14400,
				"refresh_token": "refresh-new",
			},
		)

	token = await refresh_access_token(
		HMRCEnvironment.SANDBOX,
		client_id="test-client",
		client_secret="test-secret",
		refresh_token="refresh-old",
		transport=httpx.MockTransport(handler),
	)

	assert token.access_token == "access-2"
	assert token.refresh_token == "refresh-new"
