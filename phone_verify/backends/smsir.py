# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Third Party Stuff
from sms_ir import SmsIr
from requests import ConnectionError

# Local
from .base import BaseBackend


class SmsIrBackend(BaseBackend):
    def __init__(self, **options):
        super().__init__(**options)

        # Lower case it just to be sure
        options = {key.lower(): value for key, value in options.items()}
        self._api_key = options.get("api_key", None)
        self._linenumber = options.get("linenumber", None)

        self.client = SmsIr(
            api_key=self._api_key,
            linenumber=self._linenumber,
        )
        self.exception_class = ConnectionError

    def send_sms(self, number, message):
        self.client.send_sms(
            number,
            message,
            self._linenumber,
        )

    def send_bulk_sms(self, numbers, message):
        self.client.send_bulk_sms(
            numbers,
            message,
            self._linenumber,
        )
