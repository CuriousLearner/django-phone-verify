# -*- coding: utf-8 -*-

# Third party
from django.conf import settings
from django.utils.module_loading import import_string

DEFAULT_SERVICE = 'phone_verify.backends.base.BaseBackend'

backend = None


def get_sms_backend(phone_number):
    if not backend:
        backend_import = DEFAULT_SERVICE

        if settings.PHONE_VERIFICATION.get('BACKEND', None):
            backend_import = settings.PHONE_VERIFICATION['BACKEND']

        backend_cls = import_string(backend_import)
        return backend_cls(**settings.PHONE_VERIFICATION['OPTIONS'])
