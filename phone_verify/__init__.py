# -*- coding: utf-8 -*-
import django

__version__ = "3.2.0"

if django.VERSION < (3, 2):  # pragma: no cover
    default_app_config = "phone_verify.apps.PhoneVerificationConfig"
