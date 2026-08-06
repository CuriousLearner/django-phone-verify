# -*- coding: utf-8 -*-

from datetime import timedelta

import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from freezegun import freeze_time

from phone_verify.admin import SMSVerificationAdmin
from phone_verify.models import SMSVerification

from . import factories as f

pytestmark = pytest.mark.django_db

SECURITY_CODE = "123456"
PHONE_NUMBER = "+13478379634"
SESSION_TOKEN = "phone-auth-session-token"


def test_sms_verification_is_registered_in_admin():
    model_admin = admin.site._registry[SMSVerification]

    assert isinstance(model_admin, SMSVerificationAdmin)
    for field in ("id", "security_code", "phone_number", "is_verified", "is_valid"):
        assert field in model_admin.list_display


def test_is_valid_tracks_security_code_expiry():
    """`is_valid` is the inverse of the model's expiry check."""
    verification = f.create_verification(
        security_code=SECURITY_CODE,
        phone_number=PHONE_NUMBER,
        session_token=SESSION_TOKEN,
    )
    model_admin = SMSVerificationAdmin(SMSVerification, AdminSite())

    # Test settings expire security codes after 1 second.
    with freeze_time(verification.created_at):
        assert model_admin.is_valid(verification) is True

    with freeze_time(verification.created_at + timedelta(seconds=2)):
        assert model_admin.is_valid(verification) is False
