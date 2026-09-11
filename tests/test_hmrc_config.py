from erpnext_mtd.hmrc import HMRCEnvironment


def test_sandbox_urls() -> None:
    env = HMRCEnvironment.SANDBOX

    assert env.api_base_url == "https://test-api.service.hmrc.gov.uk"
    assert env.oauth_authorize_url == "https://test-api.service.hmrc.gov.uk/oauth/authorize"
    assert env.oauth_token_url == "https://test-api.service.hmrc.gov.uk/oauth/token"

def test_production_urls() -> None:
    assert (
        HMRCEnvironment.PRODUCTION.api_base_url
        == "https://api.service.hmrc.gov.uk"
    )
