from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True, slots=True)
class OAuthToken:
	access_token: str
	token_type: str
	expires_in: int
	refresh_token: str
	scope: str | None = None
	issued_at: datetime | None = None

	@property
	def expires_at(self) -> datetime:
		if self.issued_at is None:
			return None

		return self.issued_at + timedelta(seconds=self.expires_in)

	def is_expired(self, *, now: datetime | None = None) -> bool:
		if self.expires_at is None:
			return False

		now = now or datetime.now(UTC)
		return now >= self.expires_at
