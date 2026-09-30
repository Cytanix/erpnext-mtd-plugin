# ERPNext MTD
#
# Copyright (C) 2026 Cytanix Ltd.
#
# SPDX-License-Identifier: GPL-3.0-only

from datetime import UTC, datetime
from urllib.parse import urlencode

import httpx

from .client import HMRCClient
from .config import HMRCEnvironment
from .exceptions import HMRCProtocolError
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

	return _parse_token_response(payload)


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

	return _parse_token_response(
		payload,
		fallback_refresh_token=refresh_token,
	)


def _parse_token_response(
	payload: dict[str, object],
	*,
	fallback_refresh_token: str | None = None,
) -> OAuthToken:
	access_token = payload.get("access_token")
	token_type = payload.get("token_type")
	expires_in = payload.get("expires_in")
	refresh_token = payload.get("refresh_token", fallback_refresh_token)
	scope = payload.get("scope")

	if not isinstance(access_token, str) or not access_token.strip():
		raise HMRCProtocolError("Invalid OAuth token response: access_token")

	if not isinstance(token_type, str) or not token_type.strip():
		raise HMRCProtocolError("Invalid OAuth token response: token_type")

	if not isinstance(expires_in, int) or isinstance(expires_in, bool) or expires_in <= 0:
		raise HMRCProtocolError("Invalid OAuth token response: expires_in")

	if not isinstance(refresh_token, str) or not refresh_token.strip():
		raise HMRCProtocolError("Invalid OAuth token response: refresh_token")

	if scope is not None and not isinstance(scope, str):
		raise HMRCProtocolError("Invalid OAuth token response: scope")

	return OAuthToken(
		access_token=access_token,
		token_type=token_type,
		expires_in=expires_in,
		refresh_token=refresh_token,
		scope=scope,
		issued_at=datetime.now(UTC),
	)
