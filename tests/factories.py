# -*- coding: utf-8 -*-

# Third Party Stuff
from django.apps import apps
from django_dynamic_fixture import G


def create_verification(**kwargs):
    SMSVerification = apps.get_model("phone_verify", "SMSVerification")
    verification = G(SMSVerification, **kwargs)
    return verification
