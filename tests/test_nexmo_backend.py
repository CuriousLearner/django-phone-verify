from django.urls import reverse
import pytest
from tests import test_settings

PHONE_NUMBER = "+13478379634"
SECURITY_CODE = "123456"
SESSION_TOKEN = "phone-auth-session-token"

pytestmark = pytest.mark.django_db


def test_nexmo_backend(client, mocker):
    url = reverse("phone-register")
    phone_number = PHONE_NUMBER
    data = {"phone_number": phone_number}

    mocker.patch("phone_verify.backends.base.BaseBackend.create_security_code_and_session_token",
                 return_value=(SECURITY_CODE, SESSION_TOKEN))
    mock_send_message = mocker.patch("phone_verify.backends.nexmo.nexmo.Client.send_message")

    test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["BACKEND"] = "phone_verify.backends.nexmo.NexmoBackend"
    test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["OPTIONS"]["KEY"] = "fake"

    response = client.post(url, data)
    assert response.status_code == 200

    from_number = test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["OPTIONS"]["FROM"]
    message = "Welcome to Phone Verify! Please use security code 123456 to proceed."
    test_data = {
        'from': from_number,
        'to': phone_number,
        'text': message,
    }
    mock_send_message.assert_called_once_with(test_data)

    # Assign back the Backend as defined in settings
    test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["BACKEND"] = "phone_verify.backends.twilio.TwilioBackend"


def test_nexmo_sandbox_backend(client, mocker):
    url = reverse("phone-register")
    phone_number = PHONE_NUMBER
    data = {"phone_number": phone_number}

    mocker.patch("phone_verify.backends.base.BaseBackend.generate_session_token", return_value=SESSION_TOKEN)
    mock_send_message = mocker.patch("phone_verify.backends.nexmo.nexmo.Client.send_message")

    test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["BACKEND"] = "phone_verify.backends.nexmo.NexmoSandboxBackend"
    test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["OPTIONS"]["KEY"] = "fake"

    response = client.post(url, data)
    assert response.status_code == 200

    from_number = test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["OPTIONS"]["FROM"]
    message = "Welcome to Phone Verify! Please use security code 123456 to proceed."
    test_data = {
        'from': from_number,
        'to': phone_number,
        'text': message,
    }
    mock_send_message.assert_called_once_with(test_data)

    # Assign back the Backend as defined in settings
    test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["BACKEND"] = "phone_verify.backends.twilio.TwilioBackend"
