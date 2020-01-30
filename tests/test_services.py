# -*- coding: utf-8 -*-

# Third Party Stuff
import pytest
from . import test_settings as settings

# phone_verify Stuff
from phone_verify.services import PhoneVerificationService
from . import BACKEND_SERVICES

pytestmark = pytest.mark.django_db


def test_message_generation_and_sending_service(client, mocker):
    for backend, backend_service in BACKEND_SERVICES:
        settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["BACKEND"] = backend
        api = mocker.patch(backend_service)
        service = PhoneVerificationService(phone_number="+13478379634")
        service.send_verification("+13478379634", "123456")

        assert api.assert_called_once
