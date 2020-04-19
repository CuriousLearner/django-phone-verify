# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import time

# Third party stuff
import pytest
from django.apps import apps
from django.test import override_settings
from django.urls import reverse

from conftest import backends, sandbox_backends
from . import factories as f
from .test_backends import _get_backend_cls

pytestmark = pytest.mark.django_db

SECURITY_CODE = "123456"
PHONE_NUMBER = "+13478379634"
SESSION_TOKEN = "phone-auth-session-token"


def test_phone_registration_sends_message(client, mocker, backend):
    url = reverse("phone-register")
    phone_number = PHONE_NUMBER
    data = {"phone_number": phone_number}
    twilio_api = mocker.patch(
        "phone_verify.services.PhoneVerificationService.send_verification"
    )

    response = client.post(url, data)

    assert response.status_code == 200
    assert twilio_api.called
    assert "session_token" in response.data
    SMSVerification = apps.get_model("phone_verify", "SMSVerification")
    assert SMSVerification.objects.get(
        session_token=response.data["session_token"], phone_number=phone_number
    )


def test_security_code_session_token_verification_api(client, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )
        url = reverse("phone-verify")
        data = {
            "phone_number": PHONE_NUMBER,
            "security_code": SECURITY_CODE,
            "session_token": SESSION_TOKEN,
        }
        response = client.json.post(url, data=data)
        assert response.status_code == 200
        assert response.data["message"] == "Security code is valid."


def test_phone_verification_with_incomplete_payload(client, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )
        url = reverse("phone-verify")
        data = {"phone_number": PHONE_NUMBER}
        response = client.json.post(url, data=data)
        assert response.status_code == 400
        response_data = json.loads(json.dumps(response.data))
        assert response_data["session_token"][0] == "This field is required."
        assert response_data["security_code"][0] == "This field is required."

        data = {"security_code": SECURITY_CODE}
        response = client.json.post(url, data=data)
        assert response.status_code == 400
        response_data = json.loads(json.dumps(response.data))
        assert response_data["phone_number"][0] == "This field is required."


def test_phone_verification_with_incorrect_payload(client, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )
        url = reverse("phone-verify")
        # Payload with wrong session token
        data = {
            "phone_number": PHONE_NUMBER,
            "security_code": SECURITY_CODE,
            "session_token": "wrong-session-token",
        }
        response = client.json.post(url, data=data)
        response_data = json.loads(json.dumps(response.data))

        backend_cls = _get_backend_cls(backend)

        if backend_cls in backends:
            assert response.status_code == 400
            assert response_data["non_field_errors"][0] == "Session Token mis-match"
        elif backend_cls in sandbox_backends:
            # Sandbox Backend returns a 200 status code as it does not check the payload information
            assert response.status_code == 200

        # Payload with wrong security code
        data = {
            "phone_number": PHONE_NUMBER,
            "security_code": "999999",
            "session_token": SESSION_TOKEN,
        }
        response = client.json.post(url, data=data)
        response_data = json.loads(json.dumps(response.data))
        if backend_cls in backends:
            assert response.status_code == 400
            assert response_data["non_field_errors"][0] == "Security code is not valid"
        elif backend_cls in sandbox_backends:
            # Sandbox Backend returns a 200 status code as it does not check the payload information
            assert response.status_code == 200

        # Payload with incorrect phone_number
        data = {
            "phone_number": "+13478379632",
            "security_code": SECURITY_CODE,
            "session_token": SESSION_TOKEN,
        }
        response = client.json.post(url, data=data)
        response_data = json.loads(json.dumps(response.data))
        if backend_cls in backends:
            assert response.status_code == 400
            assert response_data["non_field_errors"][0] == "Security code is not valid"
        elif backend_cls in sandbox_backends:
            # Sandbox Backend returns a 200 status code as it does not check the payload information
            assert response.status_code == 200


def test_check_security_code_expiry(client, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
        )
        time.sleep(2)
        url = reverse("phone-verify")
        data = {
            "phone_number": PHONE_NUMBER,
            "security_code": SECURITY_CODE,
            "session_token": SESSION_TOKEN,
        }
        response = client.json.post(url, data=data)
        response_data = json.loads(json.dumps(response.data))

        backend_cls = _get_backend_cls(backend)

        if backend_cls in backends:
            assert response.status_code == 400
            assert response_data["non_field_errors"][0] == "Security code has expired"
        elif backend_cls in sandbox_backends:
            # Sandbox Backend returns a 200 status code when verifying security code expiry
            assert response.status_code == 200


def test_verified_security_code(client, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        f.create_verification(
            security_code=SECURITY_CODE,
            phone_number=PHONE_NUMBER,
            session_token=SESSION_TOKEN,
            is_verified=True,
        )
        url = reverse("phone-verify")
        data = {
            "phone_number": PHONE_NUMBER,
            "security_code": SECURITY_CODE,
            "session_token": SESSION_TOKEN,
        }

        backend_cls = _get_backend_cls(backend)

        # Security code verification is restricted to one time
        backend["VERIFY_SECURITY_CODE_ONLY_ONCE"] = True
        response = client.json.post(url, data=data)
        response_data = json.loads(json.dumps(response.data))
        if backend_cls in backends:
            assert response.status_code == 400
            assert (
                response_data["non_field_errors"][0]
                == "Security code is already verified"
            )
        elif backend_cls in sandbox_backends:
            # Sandbox Backend returns a 200 status code when verifying security code
            assert response.status_code == 200

        # Security code verification is not restricted to one time
        backend["VERIFY_SECURITY_CODE_ONLY_ONCE"] = False
        response = client.json.post(url, data=data)
        response_data = json.loads(json.dumps(response.data))
        assert response.status_code == 200
        assert response.data["message"] == "Security code is valid."
