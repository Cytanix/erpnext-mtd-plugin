from urllib.parse import urlencode

from .config import HMRCEnvironment


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
