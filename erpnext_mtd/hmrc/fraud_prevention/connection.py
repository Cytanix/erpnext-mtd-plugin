from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ClientConnection:
	public_ip: str
	public_port: int
	timestamp: datetime
