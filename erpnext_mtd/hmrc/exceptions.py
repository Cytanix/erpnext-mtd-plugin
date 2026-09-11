class HMRCError(Exception):
	"""Base exception for errors communicating with HMRC."""


class HMRCRequestError(HMRCError):
	"""HMRC rejected an API request."""

	def __init__(
		self,
		status_code: int,
		code: str | None = None,
		message: str | None = None,
	) -> None:
		self.status_code = status_code
		self.code = code
		self.message = message

		detail = message or code or "Unknown HMRC API error"
		super().__init__(f"HMRC API returned HTTP {status_code}: {detail}")
