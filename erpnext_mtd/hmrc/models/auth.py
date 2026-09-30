# ERPNext MTD
#
# Copyright (C) 2026 Cytanix Ltd.
#
# SPDX-License-Identifier: GPL-3.0-only

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
	def expires_at(self) -> datetime | None:
		if self.issued_at is None:
			return None

		return self.issued_at + timedelta(seconds=self.expires_in)

	def is_expired(self, *, now: datetime | None = None) -> bool:
		expires_at = self.expires_at
		if expires_at is None:
			return True

		now = now or datetime.now(UTC)
		return now >= self.expires_at
