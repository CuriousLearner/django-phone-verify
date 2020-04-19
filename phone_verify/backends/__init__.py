# -*- coding: utf-8 -*-

# Third party
from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured

backend = None


def get_sms_backend(phone_number):
    if not backend:

        if settings.PHONE_VERIFICATION.get("BACKEND", None):
            backend_import = settings.PHONE_VERIFICATION["BACKEND"]
        else:
            raise ImproperlyConfigured(
                "Please specify BACKEND in PHONE_VERIFICATION within your settings"
            )

        backend_cls = import_string(backend_import)
        return backend_cls(**settings.PHONE_VERIFICATION["OPTIONS"])
