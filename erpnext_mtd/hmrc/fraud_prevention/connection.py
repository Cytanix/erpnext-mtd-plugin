# ERPNext MTD
#
# Copyright (C) 2026 Cytanix Ltd.
#
# SPDX-License-Identifier: GPL-3.0-only

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ClientConnection:
	public_ip: str
	public_port: int
	timestamp: datetime
