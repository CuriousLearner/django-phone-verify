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
        self._api_key = options.get("api_key", None)
        self._sender = options.get("sender", None)

        self._api = KavenegarAPI(self._api_key)

    def send_sms(self, number, message):
        try:
            params = {
                'receptor': number,
                'template': '',
                'token': message,
                'type': 'sms'
            }
            response = self._api.sms_send(params)
            print(response)
        except APIException as exp:
            print(exp)
        except HTTPException as exp:
            print(exp)

    def send_bulk_sms(self, numbers, message):
        try:
            params = {
                'sender': self._sender,
                'receptor': numbers,
                'message': message,
            }
            response = self._api.sms_sendarray(params)
            print(response)
        except APIException as exp:
            print(exp)
        except HTTPException as exp:
            print(exp)
