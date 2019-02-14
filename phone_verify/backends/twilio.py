# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Third Party Stuff
from django.conf import settings as django_settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioRestClient

# Local
from .base import BaseBackend


class TwilioBackend(BaseBackend):
    def __init__(self, **options):
        super(TwilioBackend, self).__init__(**options)
        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._sid = options.get('sid', None)
        self._secret = options.get('secret', None)  # auth_token
        self._from = options.get('from', None)

        self.client = TwilioRestClient(self._sid, self._secret)
        self.exception_class = TwilioRestException

    def send_sms(self, number, message):
        self.client.messages.create(to=number, body=message, from_=self._from)

    def send_bulk_sms(self, numbers, message):
        for number in numbers:
            self.send_sms(to=number, body=message, from_=self._from)


class TwilioSandboxBackend(BaseBackend):
    def __init__(self, **options):
        super(TwilioSandboxBackend, self).__init__(**options)
        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._sid = options.get('sid', None)
        self._secret = options.get('secret', None)  # auth_token
        self._from = options.get('from', None)
        self._token = django_settings.PHONE_VERIFICATION.get('TWILIO_SANDBOX_TOKEN')

        self.client = TwilioRestClient(self._sid, self._secret)
        self.exception_class = TwilioRestException

    def send_sms(self, number, message):
        self.client.messages.create(to=number, body=message, from_=self._from)

    def send_bulk_sms(self, numbers, message):
        for number in numbers:
            self.send_sms(to=number, body=message, from_=self._from)

    def generate_token(self):
        """
        Returns an fixed token
        """
        return self._token

    def create_temporary_token(self, number):
        """
        Creates a temporary token inside the cache, this holds the phone number
        as value, so that we can later check if everything is correct.

        :param number: Number of recipient

        :return token: string of SHA token
        """
        return self.generate_token()

    def validate_token(self, otp, phone_number):
        return self.VALID
