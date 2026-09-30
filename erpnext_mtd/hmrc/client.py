# ERPNext MTD
#
# Copyright (C) 2026 Cytanix Ltd.
#
# SPDX-License-Identifier: GPL-3.0-only

from collections.abc import Mapping
from typing import Any

import httpx

from .config import HMRCEnvironment
from .exceptions import HMRCRequestError


class HMRCClient:
	def __init__(
		self,
		environment: HMRCEnvironment,
		*,
		timeout: float = 30.0,
		transport: httpx.AsyncBaseTransport | None = None,
	) -> None:
		self.environment = environment
		self._client = httpx.AsyncClient(
			base_url=environment.api_base_url,
			timeout=timeout,
			transport=transport,
			headers={
				"Accept": "application/vnd.hmrc.1.0+json",
			},
		)

	async def __aenter__(self) -> "HMRCClient":
		return self

	async def __aexit__(self, *_: object) -> None:
		await self.aclose()

	async def aclose(self) -> None:
		await self._client.aclose()

	async def get(
		self,
		path: str,
		*,
		headers: Mapping[str, str] | None = None,
		params: Mapping[str, str] | None = None,
	) -> dict[str, Any]:
		response = await self._client.get(
			path,
			headers=headers,
			params=params,
		)

		return self._handle_response(response)

	@staticmethod
	def _handle_response(response: httpx.Response) -> dict[str, Any]:
		if response.is_success:
			if not response.content:
				return {}

			try:
				payload = response.json()
			except ValueError as exc:
				raise HMRCRequestError(
					status_code=response.status_code,
					message="HMRC returned an invalid JSON response.",
				) from exc

			if not isinstance(payload, dict):
				raise HMRCRequestError(
					status_code=response.status_code,
					message="HMRC returned an unexpected JSON response.",
				)

			return payload

		try:
			payload = response.json()
		except ValueError:
			payload = {}

		if not isinstance(payload, dict):
			payload = {}

		raise HMRCRequestError(
			status_code=response.status_code,
			code=payload.get("code") or payload.get("error"),
			message=payload.get("message") or payload.get("error_description"),
		)

	async def post(
		self,
		path: str,
		*,
		headers: Mapping[str, str] | None = None,
		data: Mapping[str, Any] | None = None,
		json: Mapping[str, Any] | None = None,
	) -> dict[str, Any]:
		response = await self._client.post(
			path,
			headers=headers,
			data=data,
			json=json,
		)

		return self._handle_response(response)
