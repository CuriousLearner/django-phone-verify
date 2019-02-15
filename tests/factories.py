# -*- coding: utf-8 -*-

# Third Party Stuff
import pytest
from django_dynamic_fixture import G

from django.apps import apps


def create_verification(**kwargs):
    SMSVerification = apps.get_model('phone_verify', 'SMSVerification')
    verification = G(SMSVerification, **kwargs)
    return verification
