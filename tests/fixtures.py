import pytest

from phone_verify.backends.base import BaseBackend
from phone_verify.backends.nexmo import NexmoBackend, NexmoSandboxBackend
from phone_verify.backends.twilio import TwilioBackend, TwilioSandboxBackend


@pytest.fixture(
    params=[
        BaseBackend,
        NexmoBackend,
        NexmoSandboxBackend,
        TwilioBackend,
        TwilioSandboxBackend,
    ]
)
def VerificationBackend(request):
    return request.param
