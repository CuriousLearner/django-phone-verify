from django.urls import reverse
import pytest
from tests import test_settings

PHONE_NUMBER = "+13478379634"
SECURITY_CODE = "123456"
SESSION_TOKEN = "phone-auth-session-token"

pytestmark = pytest.mark.django_db


def test_twilio_backend(client, mocker):
    url = reverse("phone-register")
    phone_number = PHONE_NUMBER
    data = {"phone_number": phone_number}

    mocker.patch("phone_verify.backends.base.BaseBackend.create_security_code_and_session_token",
                 return_value=(SECURITY_CODE, SESSION_TOKEN))
    mock_twilio_messages = mocker.patch("phone_verify.backends.twilio.TwilioRestClient.messages")
    mock_twilio_messages.create = mocker.MagicMock()

    response = client.post(url, data)
    assert response.status_code == 200

    from_number = test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["OPTIONS"]["FROM"]
    message = "Welcome to Phone Verify! Please use security code 123456 to proceed."

    mock_twilio_messages.create.assert_called_once_with(to=phone_number, body=message, from_=from_number)


def test_twilio_sandbox_backend(client, mocker):
    url = reverse("phone-register")
    phone_number = PHONE_NUMBER
    data = {"phone_number": phone_number}

    mocker.patch("phone_verify.backends.base.BaseBackend.generate_session_token", return_value=SESSION_TOKEN)
    mock_twilio_messages = mocker.patch("phone_verify.backends.twilio.TwilioRestClient.messages")
    mock_twilio_messages.create = mocker.MagicMock()

    test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["BACKEND"] = "phone_verify.backends.twilio.TwilioSandboxBackend"

    response = client.post(url, data)
    assert response.status_code == 200

    from_number = test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["OPTIONS"]["FROM"]
    message = "Welcome to Phone Verify! Please use security code 123456 to proceed."

    mock_twilio_messages.create.assert_called_once_with(to=phone_number, body=message, from_=from_number)

    # Assign back the Backend as defined in settings
    test_settings.DJANGO_SETTINGS["PHONE_VERIFICATION"]["BACKEND"] = "phone_verify.backends.twilio.TwilioBackend"
