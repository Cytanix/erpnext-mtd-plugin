from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

from erpnext_mtd.hmrc.config import HMRCEnvironment
from erpnext_mtd.hmrc.models import OAuthToken
from erpnext_mtd.hmrc.oauth import build_authorization_url


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
