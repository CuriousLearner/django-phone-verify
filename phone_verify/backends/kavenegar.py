# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Third Party Stuff
from kavenegar import KavenegarAPI, APIException, HTTPException

# Local
from phone_verify.models import SMSVerification
from .base import BaseBackend


class KavenegarException(HTTPException, APIException):
    pass


class KavenegarBackend(BaseBackend):
    def __init__(self, **options):
        super().__init__(**options)
        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._api_key = options.get("secret", None)
        self._sender = options.get("from", None)

        self.client = KavenegarAPI(self._api_key)
        self.exception_class = KavenegarException

    def send_sms(self, number, message):
        params = {'sender': self._sender, 'receptor': number, 'message': message, }
        self.client.sms_send(params)

    def send_bulk_sms(self, numbers, message):
        params = {'sender': self._sender, 'receptor': numbers, 'message': message, }
        self.client.sms_sendarray(params)


class KavenegarSandboxBackend(BaseBackend):
    def __init__(self, **options):
        super().__init__(**options)
        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._api_key = options.get("secret", None)
        self._sender = options.get("from", None)

        self.client = KavenegarAPI(self._api_key)
        self.exception_class = KavenegarException

    def send_sms(self, number, message):
        params = {'sender': self._sender, 'receptor': number, 'message': message, }
        self.client.sms_send(params)

    def send_bulk_sms(self, numbers, message):
        params = {'sender': self._sender, 'receptor': numbers, 'message': message, }
        self.client.sms_sendarray(params)

    def generate_security_code(self):
        """
        Returns a fixed security code
        """
        return self._token

    def validate_security_code(self, security_code, phone_number, session_token):
        return SMSVerification.objects.none(), self.SECURITY_CODE_VALID
