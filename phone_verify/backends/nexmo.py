# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Third Party Stuff
import nexmo
from nexmo.errors import ClientError

# Local
from .base import BaseBackend
from phone_verify.models import SMSVerification


class NexmoBackend(BaseBackend):
    def __init__(self, **options):
        super().__init__(**options)

        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._key = options.get("key", None)
        self._secret = options.get("secret", None)
        self._from = options.get("from", None)

        self.client = nexmo.Client(key=self._key, secret=self._secret)
        self.exception_class = ClientError

    def send_sms(self, number, message):
        self.client.send_message({"from": self._from, "to": number, "text": message})

    def send_bulk_sms(self, numbers, message):
        for number in numbers:
            self.send_sms(number=number, message=message)


class NexmoSandboxBackend(BaseBackend):
    def __init__(self, **options):
        super().__init__(**options)
        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._key = options.get("key", None)
        self._secret = options.get("secret", None)
        self._from = options.get("from", None)
        self._token = options.get("sandbox_token", None)

        self.client = nexmo.Client(key=self._key, secret=self._secret)
        self.exception_class = ClientError

    def send_sms(self, number, message):
        self.client.send_message({"from": self._from, "to": number, "text": message})

    def send_bulk_sms(self, numbers, message):
        for number in numbers:
            self.send_sms(number=number, message=message)

    def generate_security_code(self):
        """
        Returns a fixed security code
        """
        return self._token

    def validate_security_code(self, security_code, phone_number, session_token):
        return SMSVerification.objects.none(), self.SECURITY_CODE_VALID
