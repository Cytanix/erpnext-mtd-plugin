import pytest

from erpnext_mtd.hmrc.state import OAuthStateError, create_state, validate_state

secret = b"supersecretpassworddontshareidk"

def test_state_round_trip() -> None:
	state = create_state(company="Cytanix Ltd", secret=secret)

	payload = validate_state(state, secret=secret)

	assert payload.company == "Cytanix Ltd"


def test_tampered_state_is_rejected() -> None:
	state = create_state(company="Cytanix Ltd", secret=secret)
	tampered = state[:-1] + ("A" if state[-1] != "A" else "B")

	with pytest.raises(OAuthStateError):
		validate_state(tampered, secret=secret)
