# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Third party stuff
import json
import time

import pytest
from django.apps import apps
from django.urls import reverse

from . import test_settings as settings
from . import factories as f

pytestmark = pytest.mark.django_db

SECURITY_CODE = "123456"
PHONE_NUMBER = "+13478379634"
SESSION_CODE = "phone-auth-session-code"


def test_phone_registration_sends_message(client, mocker):
    url = reverse("phone-register")
    phone_number = PHONE_NUMBER
    data = {"phone_number": phone_number}
    twilio_api = mocker.patch(
        "phone_verify.services.PhoneVerificationService.send_verification"
    )

    response = client.post(url, data)

    assert response.status_code == 200
    assert twilio_api.called
    assert "session_code" in response.data
    SMSVerification = apps.get_model("phone_verify", "SMSVerification")
    assert SMSVerification.objects.get(
        session_code=response.data["session_code"], phone_number=phone_number
    )


def test_security_code_session_code_verification_api(client):
    f.create_verification(
        security_code=SECURITY_CODE,
        phone_number=PHONE_NUMBER,
        session_code=SESSION_CODE,
    )
    url = reverse("phone-verify")
    data = {
        "phone_number": PHONE_NUMBER,
        "security_code": SECURITY_CODE,
        "session_code": SESSION_CODE,
    }
    response = client.json.post(url, data=data)
    assert response.status_code == 200
    assert response.data["message"] == "Security code is valid."


def test_phone_verification_with_incomplete_payload(client):
    f.create_verification(
        security_code=SECURITY_CODE,
        phone_number=PHONE_NUMBER,
        session_code=SESSION_CODE,
    )
    url = reverse("phone-verify")
    data = {"phone_number": PHONE_NUMBER}
    response = client.json.post(url, data=data)
    assert response.status_code == 400
    response_data = json.loads(json.dumps(response.data))
    assert response_data["session_code"][0] == "This field is required."
    assert response_data["security_code"][0] == "This field is required."

    data = {"security_code": SECURITY_CODE}
    response = client.json.post(url, data=data)
    assert response.status_code == 400
    response_data = json.loads(json.dumps(response.data))
    assert response_data["phone_number"][0] == "This field is required."


def test_phone_verification_with_incorrect_payload(client):
    f.create_verification(
        security_code=SECURITY_CODE,
        phone_number=PHONE_NUMBER,
        session_code=SESSION_CODE,
    )
    url = reverse("phone-verify")
    # Payload with wrong session code
    data = {
        "phone_number": PHONE_NUMBER,
        "security_code": SECURITY_CODE,
        "session_code": "wrong-session-code",
    }
    response = client.json.post(url, data=data)
    response_data = json.loads(json.dumps(response.data))
    assert response.status_code == 400
    assert response_data["non_field_errors"][0] == "Session Code mis-match"

    # Payload with wrong security code
    data = {
        "phone_number": PHONE_NUMBER,
        "security_code": "999999",
        "session_code": SESSION_CODE,
    }
    response = client.json.post(url, data=data)
    assert response.status_code == 400
    response_data = json.loads(json.dumps(response.data))
    assert response_data["non_field_errors"][0] == "Security code is not valid"

    # Payload with incorrect phone_number
    data = {
        "phone_number": "+13478379632",
        "security_code": SECURITY_CODE,
        "session_code": SESSION_CODE,
    }
    response = client.json.post(url, data=data)
    assert response.status_code == 400
    response_data = json.loads(json.dumps(response.data))
    assert response_data["non_field_errors"][0] == "Security code is not valid"


def test_security_code_expired(client):
    f.create_verification(
        security_code=SECURITY_CODE,
        phone_number=PHONE_NUMBER,
        session_code=SESSION_CODE,
    )
    time.sleep(2)
    url = reverse("phone-verify")
    data = {
        "phone_number": PHONE_NUMBER,
        "security_code": SECURITY_CODE,
        "session_code": SESSION_CODE,
    }
    response = client.json.post(url, data=data)
    assert response.status_code == 400
    response_data = json.loads(json.dumps(response.data))
    assert response_data["non_field_errors"][0] == "Security code has expired"


def test_verified_security_code(client):
    f.create_verification(
        security_code=SECURITY_CODE, phone_number=PHONE_NUMBER, session_code=SESSION_CODE, is_verified=True
    )
    url = reverse("phone-verify")
    data = {"phone_number": PHONE_NUMBER, "security_code": SECURITY_CODE, "session_code": SESSION_CODE}

    # Security code verification is restricted to one time
    settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["VERIFY_SECURITY_CODE_ONLY_ONCE"] = True
    response = client.json.post(url, data=data)
    response_data = json.loads(json.dumps(response.data))
    assert response.status_code == 400
    assert response_data["non_field_errors"][0] == "Security code is already verified"

    # Security code verification is not restricted to one time
    settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["VERIFY_SECURITY_CODE_ONLY_ONCE"] = False
    response = client.json.post(url, data=data)
    response_data = json.loads(json.dumps(response.data))
    assert response.status_code == 200
    assert response.data["message"] == "Security code is valid."
