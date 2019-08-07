# -*- coding: utf-8 -*-

from django.apps import apps

# Third Party Stuff
from django_dynamic_fixture import G


def create_verification(**kwargs):
    SMSVerification = apps.get_model("phone_verify", "SMSVerification")
    verification = G(SMSVerification, **kwargs)
    return verification
