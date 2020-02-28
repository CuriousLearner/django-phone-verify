"""
This module is used to provide configuration, fixtures, and plugins for pytest.
It may be also used for extending doctest's context:
1. https://docs.python.org/3/library/doctest.html
2. https://docs.pytest.org/en/latest/doctest.html
"""

# Standard Library
import copy
import functools

# Third Party Stuff
import pytest
import django
from django.conf import settings

from tests import test_settings

backends = {"twilio.TwilioBackend", "nexmo.NexmoBackend"}
sandbox_backends = {"twilio.TwilioSandboxBackend", "nexmo.NexmoSandboxBackend"}
all_backends = list(backends) + list(sandbox_backends)


class PartialMethodCaller:
    def __init__(self, obj, **partial_params):
        self.obj = obj
        self.partial_params = partial_params

    def __getattr__(self, name):
        return functools.partial(getattr(self.obj, name), **self.partial_params)


@pytest.fixture
def client():
    """Django Test Client, with some convenient overriden methods.
    """
    from django.test import Client

    class _Client(Client):
        @property
        def json(self):
            """Add json method on the client for sending json type request.

            Usages:
            >>> import json
            >>> url = reverse("phone-verify")
            >>> client.json.get(url)
            >>> client.json.post(url, data=json.dumps(payload))
            """
            return PartialMethodCaller(
                obj=self, content_type='application/json;charset="utf-8"'
            )

    return _Client()


@pytest.fixture(params=all_backends)
def backend(request):
    phone_verification_settings = copy.deepcopy(
        test_settings.DJANGO_SETTINGS.get("PHONE_VERIFICATION")
    )
    phone_verification_settings["BACKEND"] = f"phone_verify.backends.{request.param}"
    if (
        request.param == "nexmo.NexmoSandboxBackend"
        or request.param == "nexmo.NexmoBackend"
    ):
        phone_verification_settings["OPTIONS"]["KEY"] = "fake"
    return phone_verification_settings


def pytest_configure():
    from tests import test_settings

    settings.configure(**test_settings.DJANGO_SETTINGS)
    django.setup()
