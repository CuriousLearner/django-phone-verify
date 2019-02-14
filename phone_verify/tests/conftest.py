"""
This module is used to provide configuration, fixtures, and plugins for pytest.
It may be also used for extending doctest's context:
1. https://docs.python.org/3/library/doctest.html
2. https://docs.pytest.org/en/latest/doctest.html
"""

# Standard Library
import functools

# Third Party Stuff
import pytest
from unittest import mock


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
            >>> url = reverse("api-login")
            >>> client.json.get(url)
            >>> client.json.post(url, data=json.dumps(payload))
            """
            return PartialMethodCaller(obj=self, content_type='application/json;charset="utf-8"')

    return _Client()
