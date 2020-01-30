# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Third Party Stuff
from kavenegar import KavenegarAPI, APIException, HTTPException

# Local
from .base import BaseBackend


class KavenegarBackend(BaseBackend):
    def __init__(self, **options):
        super(KavenegarBackend, self).__init__(**options)
        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self.api_key = options.get("secret", None)
        self.sender = options.get("from", None)

        self.client = KavenegarAPI(self.api_key)
        self.exception_class = APIException, HTTPException

    def send_sms(self, number, message):
        params = {'receptor': number, 'template': '', 'token': message, 'type': 'sms'}
        self.client.sms_send(params)

    def send_bulk_sms(self, numbers, message):
        params = {'sender': self.sender, 'receptor': numbers, 'message': message, }
        self.client.sms_sendarray(params)
