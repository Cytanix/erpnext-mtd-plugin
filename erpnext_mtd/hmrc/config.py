from enum import StrEnum


class HMRCEnvironment(StrEnum):
	SANDBOX = "Sandbox"
	PRODUCTION = "Production"

	@property
	def api_base_url(self) -> str:
		return {
			HMRCEnvironment.SANDBOX: "https://test-api.service.hmrc.gov.uk",
			HMRCEnvironment.PRODUCTION: "https://api.service.hmrc.gov.uk",
		}[self]

	@property
	def oauth_authorize_url(self) -> str:
		return {
			HMRCEnvironment.SANDBOX: "https://test-www.tax.service.gov.uk/oauth/authorize",
			HMRCEnvironment.PRODUCTION: "https://www.tax.service.gov.uk/oauth/authorize",
		}[self]

	@property
	def oauth_token_url(self) -> str:
		return f"{self.api_base_url}/oauth/token"
