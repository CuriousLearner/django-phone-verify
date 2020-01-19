# -*- coding: utf-8 -*-

# Third Party Stuff
import pytest
from django.conf import settings

# phone_verify Stuff
from phone_verify.services import PhoneVerificationService

pytestmark = pytest.mark.django_db


def test_message_generation_and_sending_service(client, mocker):
	service = PhoneVerificationService(phone_number="+13478379634")
	service_api = mocker.patch(f'{settings.PHONE_VERIFICATION["DEFAULT"]["BACKEND"]}.send_sms')
	service.send_verification("+13478379634", "123456")

	assert service_api.called
