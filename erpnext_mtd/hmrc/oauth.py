from datetime import UTC, datetime
from urllib.parse import urlencode

import httpx

from .client import HMRCClient
from .config import HMRCEnvironment
from .models import OAuthToken


def build_authorization_url(
	environment: HMRCEnvironment,
	client_id: str,
	redirect_uri: str,
	scopes: tuple[str, ...],
	state: str,
) -> str:
	query = urlencode(
		{
			"response_type": "code",
			"client_id": client_id,
			"redirect_uri": redirect_uri,
			"scope": " ".join(scopes),
			"state": state,
		}
	)
	return f"{environment.oauth_authorize_url}?{query}"


async def exchange_authorization_code(
	environment: HMRCEnvironment,
	*,
	client_id: str,
	client_secret: str,
	code: str,
	redirect_uri: str,
	transport: httpx.AsyncHTTPTransport | None = None,
) -> OAuthToken:
	async with HMRCClient(environment, transport=transport) as client:
		payload = await client.post(
			"/oauth/token",
			data={
				"grant_type": "authorization_code",
				"client_id": client_id,
				"redirect_uri": redirect_uri,
				"client_secret": client_secret,
				"code": code,
			},
		)

	return OAuthToken(
		access_token=payload["access_token"],
		token_type=payload["token_type"],
		expires_in=payload["expires_in"],
		refresh_token=payload["refresh_token"],
		scope=payload.get("scope"),
		issued_at=datetime.now(UTC),
	)

async def refresh_access_token(
	environment: HMRCEnvironment,
	*,
	client_id: str,
	client_secret: str,
	refresh_token: str,
	transport: httpx.AsyncHTTPTransport | None = None,
) -> OAuthToken:
	async with HMRCClient(environment, transport=transport) as client:
		payload = await client.post(
			"/oauth/token",
			data={
				"grant_type": "refresh_token",
				"client_id": client_id,
				"client_secret": client_secret,
				"refresh_token": refresh_token,
			},
		)

	return OAuthToken(
		access_token=payload["access_token"],
		token_type=payload["token_type"],
		expires_in=payload["expires_in"],
		refresh_token=payload.get("refresh_token", refresh_token),
		scope=payload.get("scope"),
		issued_at=datetime.now(UTC),
	)
