# -*- coding: utf-8 -*-

# Third Party Stuff
from django.apps import apps
from django_dynamic_fixture import G


def create_verification(**kwargs):
    sms_verification = apps.get_model("phone_verify", "SMSVerification")
    verification = G(sms_verification, **kwargs)
    return verification
