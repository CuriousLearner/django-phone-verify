# -*- coding: utf-8 -*-

# Third party
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

backend = None


def get_sms_backend(phone_number):
    if not backend:

        if settings.PHONE_VERIFICATION.get("BACKEND", None):
            backend_import_path = settings.PHONE_VERIFICATION["BACKEND"]
        else:
            raise ImproperlyConfigured(
                "Please specify BACKEND in PHONE_VERIFICATION within your settings"
            )

        try:
            backend_cls = import_string(backend_import_path)
        except ImportError as e:
            if not any(provider in backend_import_path.lower() for provider in ['twilio', 'nexmo']):
                # Error for custom backends
                raise RuntimeError(f"Failed to import the specified backend: {backend_import_path}. Ensure the module is installed and properly configured.") from e

            # Extract the module name (e.g., 'twilio' or 'nexmo') for a more meaningful error message
            dependency_name = backend_import_path.split(".")[-2]

            # Raise an error with the correct dependency name
            raise RuntimeError(f"{dependency_name.capitalize()} backend is not installed. Please install '{dependency_name}' to use this provider.") from e

        return backend_cls(**settings.PHONE_VERIFICATION["OPTIONS"])
