from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from phone_verify.models import SMSVerification
from tests import factories as f

pytestmark = pytest.mark.django_db

SECURITY_CODE = "123456"
PHONE_NUMBER = "+13478379634"
SESSION_TOKEN = "phone-auth-session-token"


def test_cleanup_phone_verifications_no_old_records(backend):
    """Test cleanup command when no old records exist."""
    backend_copy = backend.copy()
    backend_copy["RECORD_RETENTION_DAYS"] = 30

    with override_settings(PHONE_VERIFICATION=backend_copy):
        f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )

        out = StringIO()
        call_command("cleanup_phone_verifications", stdout=out)

        assert "No verification records older than 30 days found" in out.getvalue()
        assert SMSVerification.objects.count() == 1


def test_cleanup_phone_verifications_deletes_old_records(backend):
    """Test cleanup command deletes old records."""
    backend_copy = backend.copy()
    backend_copy["RECORD_RETENTION_DAYS"] = 30

    with override_settings(PHONE_VERIFICATION=backend_copy):
        recent_verification = f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )

        old_verification = f.create_verification(
            security_code="654321",
            phone_number="+13478379633",
            session_token="old-session-token",
        )

        old_date = timezone.now() - timedelta(days=31)
        SMSVerification.objects.filter(id=old_verification.id).update(created_at=old_date)

        assert SMSVerification.objects.count() == 2

        out = StringIO()
        call_command("cleanup_phone_verifications", stdout=out)

        assert "Successfully deleted 1 verification record(s)" in out.getvalue()
        assert SMSVerification.objects.count() == 1
        assert SMSVerification.objects.filter(id=recent_verification.id).exists()
        assert not SMSVerification.objects.filter(id=old_verification.id).exists()


def test_cleanup_phone_verifications_custom_days(backend):
    """Test cleanup command with custom days parameter."""
    with override_settings(PHONE_VERIFICATION=backend):
        verification = f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )

        old_date = timezone.now() - timedelta(days=8)
        SMSVerification.objects.filter(id=verification.id).update(created_at=old_date)

        out = StringIO()
        call_command("cleanup_phone_verifications", days=7, stdout=out)

        assert "Successfully deleted 1 verification record(s) older than 7 days" in out.getvalue()
        assert SMSVerification.objects.count() == 0


def test_cleanup_phone_verifications_dry_run(backend):
    """Test cleanup command with dry-run flag."""
    backend_copy = backend.copy()
    backend_copy["RECORD_RETENTION_DAYS"] = 30

    with override_settings(PHONE_VERIFICATION=backend_copy):
        verification = f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )

        old_date = timezone.now() - timedelta(days=31)
        SMSVerification.objects.filter(id=verification.id).update(created_at=old_date)

        out = StringIO()
        call_command("cleanup_phone_verifications", dry_run=True, stdout=out)

        output = out.getvalue()
        assert "DRY RUN" in output
        assert "Would delete 1 verification record(s)" in output
        assert SMSVerification.objects.count() == 1
