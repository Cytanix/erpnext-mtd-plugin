import httpx
import pytest

from erpnext_mtd.hmrc.client import HMRCClient
from erpnext_mtd.hmrc.config import HMRCEnvironment
from erpnext_mtd.hmrc.exceptions import HMRCRequestError


@pytest.mark.asyncio
async def test_get_success() -> None:
	async def handler(request: httpx.Request) -> httpx.Response:
		assert request.url.path == "/hello"

		return httpx.Response(
			200,
			json={"message": "ok"},
		)

	transport = httpx.MockTransport(handler)

	async with HMRCClient(HMRCEnvironment.SANDBOX, transport=transport) as client:
		response = await client.get("/hello")

	assert response == {"message": "ok"}


@pytest.mark.asyncio
async def test_json_error_response() -> None:
	async def handler(request: httpx.Request) -> httpx.Response:
		return httpx.Response(
			400,
			json={
				"code": "INVALID_REQUEST",
				"message": "Something went wrong",
			},
		)

	transport = httpx.MockTransport(handler)

	async with HMRCClient(HMRCEnvironment.SANDBOX, transport=transport) as client:
		with pytest.raises(HMRCRequestError) as exc:
			await client.get("/broken")

	assert exc.value.status_code == 400
	assert exc.value.code == "INVALID_REQUEST"
	assert exc.value.message == "Something went wrong"


@pytest.mark.asyncio
async def test_non_json_error_response() -> None:
	async def handler(request: httpx.Request) -> httpx.Response:
		return httpx.Response(
			500,
			text="Internal Server Error",
		)

	transport = httpx.MockTransport(handler)

	async with HMRCClient(HMRCEnvironment.SANDBOX, transport=transport) as client:
		with pytest.raises(HMRCRequestError) as exc:
			await client.get("/explode")

	assert exc.value.status_code == 500
	assert exc.value.code is None
	assert exc.value.message is None
