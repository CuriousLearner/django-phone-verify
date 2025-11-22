from datetime import timedelta

import pytest
from django.test import override_settings
from django.utils import timezone
from freezegun import freeze_time

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


def test_sms_verification_is_expired_false(backend):
    """Test that a newly created verification is not expired."""
    with override_settings(PHONE_VERIFICATION=backend):
        sms_verification = f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )
        assert sms_verification.is_expired is False


def test_sms_verification_is_expired_true(backend):
    """Test that an old verification is expired."""
    backend_copy = backend.copy()
    backend_copy["SECURITY_CODE_EXPIRATION_SECONDS"] = 1

    with override_settings(PHONE_VERIFICATION=backend_copy):
        sms_verification = f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )

        # Move time forward 2 seconds (past the 1-second expiration)
        two_seconds_later = timezone.now() + timedelta(seconds=2)
        with freeze_time(two_seconds_later):
            assert sms_verification.is_expired is True


def test_sms_verification_is_expired_custom_expiration_time(backend):
    """Test is_expired with custom expiration time."""
    backend_copy = backend.copy()
    backend_copy["SECURITY_CODE_EXPIRATION_SECONDS"] = 300

    with override_settings(PHONE_VERIFICATION=backend_copy):
        sms_verification = f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )

        # Move time forward 301 seconds (past the 300-second expiration)
        after_expiration = timezone.now() + timedelta(seconds=301)
        with freeze_time(after_expiration):
            assert sms_verification.is_expired is True

        # Move time forward 200 seconds (before the 300-second expiration)
        before_expiration = timezone.now() + timedelta(seconds=200)
        with freeze_time(before_expiration):
            assert sms_verification.is_expired is False


def test_sms_verification_is_expired_with_deprecated_setting_name(backend):
    """Test is_expired with deprecated SECURITY_CODE_EXPIRATION_TIME setting."""
    # Remove the new setting name and use the old one
    backend_copy = backend.copy()
    del backend_copy["SECURITY_CODE_EXPIRATION_SECONDS"]
    backend_copy["SECURITY_CODE_EXPIRATION_TIME"] = 1

    with override_settings(PHONE_VERIFICATION=backend_copy):
        sms_verification = f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )

        # Move time forward 2 seconds (past the 1-second expiration)
        two_seconds_later = timezone.now() + timedelta(seconds=2)
        with freeze_time(two_seconds_later):
            assert sms_verification.is_expired is True


def test_sms_verification_new_setting_takes_precedence(backend):
    """Test that SECURITY_CODE_EXPIRATION_SECONDS takes precedence over deprecated setting."""
    backend_copy = backend.copy()
    # Set new setting to expire quickly and old setting to never expire
    backend_copy["SECURITY_CODE_EXPIRATION_SECONDS"] = 1
    backend_copy["SECURITY_CODE_EXPIRATION_TIME"] = 9999

    with override_settings(PHONE_VERIFICATION=backend_copy):
        sms_verification = f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )

        future_time = timezone.now() + timedelta(seconds=2)
        with freeze_time(future_time):
            # Should use the new setting (1 second), so should be expired
            assert sms_verification.is_expired is True
