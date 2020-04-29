import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.urls import reverse
from django.utils.module_loading import import_string

from conftest import sandbox_backends
from phone_verify.backends.base import BaseBackend

PHONE_NUMBER = "+13478379634"
SECURITY_CODE = "123456"
SESSION_TOKEN = "phone-auth-session-token"

pytestmark = pytest.mark.django_db


def _get_backend_cls(backend):
    backend_import_path = backend.get("BACKEND")
    backend_cls = backend_import_path.split("phone_verify.backends.")[1]
    return backend_cls


def test_backends(client, mocker, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        url = reverse("phone-register")
        phone_number = PHONE_NUMBER
        data = {"phone_number": phone_number}

        mocker.patch(
            "phone_verify.backends.base.BaseBackend.generate_session_token",
            return_value=SESSION_TOKEN,
        )
        mocker.patch(
            "phone_verify.backends.base.BaseBackend.generate_security_code",
            return_value=SECURITY_CODE,
        )
        message = "Welcome to Phone Verify! Please use security code 123456 to proceed."
        from_number = settings.PHONE_VERIFICATION["OPTIONS"]["FROM"]

        backend_cls = _get_backend_cls(backend)

        if (
            backend_cls == "nexmo.NexmoBackend"
            or backend_cls == "nexmo.NexmoSandboxBackend"
        ):
            # Mock the nexmo client
            mock_nexmo_send_message = mocker.patch(
                "phone_verify.backends.nexmo.nexmo.Client.send_message"
            )
            test_data = {"from": from_number, "to": phone_number, "text": message}
        elif (
            backend_cls == "twilio.TwilioBackend"
            or backend_cls == "twilio.TwilioSandboxBackend"
        ):
            # Mock the twilio client
            mock_twilio_send_message = mocker.patch(
                "phone_verify.backends.twilio.TwilioRestClient.messages"
            )
            mock_twilio_send_message.create = mocker.MagicMock()

        response = client.post(url, data)
        assert response.status_code == 200

        if backend_cls == "nexmo.NexmoBackend":
            mock_nexmo_send_message.assert_called_once_with(test_data)
        elif backend_cls == "twilio.TwilioBackend":
            mock_twilio_send_message.create.assert_called_once_with(
                to=phone_number, body=message, from_=from_number
            )

        # Get the last part of the backend and check if that is a Sandbox Backend
        if backend_cls in sandbox_backends:
            url = reverse("phone-verify")
            data = {
                "phone_number": phone_number,
                "session_token": SESSION_TOKEN,
                "security_code": SECURITY_CODE,
            }

            response = client.post(url, data)
            assert response.status_code == 200
            response_data = {"message": "Security code is valid."}
            assert response.data == response_data


def test_error_raised_when_no_backend_specified(client, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        settings.PHONE_VERIFICATION["BACKEND"] = None
        url = reverse("phone-register")
        phone_number = PHONE_NUMBER
        data = {"phone_number": phone_number}
        with pytest.raises(ImproperlyConfigured) as exc:
            client.post(url, data)
            assert (
                exc.info
                == "Please specify BACKEND in PHONE_VERIFICATION within your settings"
            )


def test_send_bulk_sms(client, mocker, backend):
    with override_settings(PHONE_VERIFICATION=backend):
        backend_import = settings.PHONE_VERIFICATION["BACKEND"]
        backend_cls = import_string(backend_import)
        cls_obj = backend_cls(**settings.PHONE_VERIFICATION["OPTIONS"])

        mock_send_sms = mocker.patch(f"{backend_import}.send_sms")
        numbers = ["+13478379634", "+13478379633", "+13478379632"]
        message = "Fake message"

        cls_obj.send_bulk_sms(numbers, message)
        assert mock_send_sms.called
        assert mock_send_sms.call_count == 3
        mock_send_sms.assert_has_calls(
            [
                mocker.call(number=numbers[0], message=message),
                mocker.call(number=numbers[1], message=message),
                mocker.call(number=numbers[2], message=message),
            ]
        )


class TestBaseBackend(BaseBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def test_base_backend_abstract_methods(mocker):
    abstract_methods = BaseBackend.__abstractmethods__
    TestBaseBackend.__abstractmethods__ = frozenset()
    cls_obj = TestBaseBackend()

    for method in abstract_methods:
        with pytest.raises(NotImplementedError):
            # This might fail in case, we have methods having different
            # number of arguments
            getattr(cls_obj, method)(mocker.Mock(), mocker.Mock())
