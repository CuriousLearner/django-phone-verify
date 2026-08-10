# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Local
from .base import BaseBackend


class TestBackend(BaseBackend):

    def send_sms(self, number, message):
        print("Test SMS to={} body={}".format(number, message))

    def send_bulk_sms(self, numbers, message):
        for number in numbers:
            self.send_sms(number=number, message=message)
