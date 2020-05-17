import pytest

from tests import factories as f

pytestmark = pytest.mark.django_db

SECURITY_CODE = "123456"
PHONE_NUMBER = "+13478379634"
SESSION_TOKEN = "phone-auth-session-token"


def test_create_sms_verification(client, mocker, backend):
    sms_verification = f.create_verification(
        security_code=SECURITY_CODE,
        phone_number=PHONE_NUMBER,
        session_token=SESSION_TOKEN,
    )
    assert str(sms_verification) == f"{PHONE_NUMBER}: {SECURITY_CODE}"
