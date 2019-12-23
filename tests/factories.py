# -*- coding: utf-8 -*-

from django.apps import apps

# Third Party Stuff
from django_dynamic_fixture import G


def create_verification(**kwargs):
    sms_verification = apps.get_model("phone_verify", "SMSVerification")
    verification = G(sms_verification, **kwargs)
    return verification
