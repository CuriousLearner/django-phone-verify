# -*- coding: utf-8 -*-

# Third Party Stuff
import pytest
from django.test import override_settings

# phone_verify Stuff
from phone_verify.services import PhoneVerificationService

pytestmark = pytest.mark.django_db


def test_message_generation_and_sending_service(client, mocker, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        service = PhoneVerificationService(phone_number="+13478379634")
        backend_service = backend.get("BACKEND")
        mock_api = mocker.patch(f"{backend_service}.send_sms")
        service.send_verification("+13478379634", "123456")

        assert mock_api.called
