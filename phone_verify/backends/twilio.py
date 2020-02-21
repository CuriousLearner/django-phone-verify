# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Third Party Stuff
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioRestClient

# Local
from .base import BaseBackend
from phone_verify.models import SMSVerification


class TwilioBackend(BaseBackend):
    def __init__(self, **options):
        super(TwilioBackend, self).__init__(**options)
        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._sid = options.get("sid", None)
        self._secret = options.get("secret", None)  # auth_token
        self._from = options.get("from", None)

        self.client = TwilioRestClient(self._sid, self._secret)
        self.exception_class = TwilioRestException

    def send_sms(self, number, message):
        self.client.messages.create(to=number, body=message, from_=self._from)

    def send_bulk_sms(self, numbers, message):
        for number in numbers:
            self.send_sms(number=number, message=message)


class TwilioSandboxBackend(BaseBackend):
    def __init__(self, **options):
        super(TwilioSandboxBackend, self).__init__(**options)
        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._sid = options.get("sid", None)
        self._secret = options.get("secret", None)  # auth_token
        self._from = options.get("from", None)
        self._token = options.get("sandbox_token")

        self.client = TwilioRestClient(self._sid, self._secret)
        self.exception_class = TwilioRestException

    def send_sms(self, number, message):
        self.client.messages.create(to=number, body=message, from_=self._from)

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
