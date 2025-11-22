# -*- coding: utf-8 -*-
"""
Constants and default values for phone_verify.
"""

import warnings

from django.conf import settings as django_settings

DEFAULT_TOKEN_LENGTH = 6
DEFAULT_MIN_TOKEN_LENGTH = 6
DEFAULT_MAX_FAILED_ATTEMPTS = 5
DEFAULT_SECURITY_CODE_EXPIRATION_SECONDS = 600  # 10 minutes
DEFAULT_RECORD_RETENTION_DAYS = 30  # Days to retain SMS verification records


def get_security_code_expiration():
    """
    Get security code expiration time in seconds.

    Checks for SECURITY_CODE_EXPIRATION_SECONDS (preferred) first,
    then falls back to SECURITY_CODE_EXPIRATION_TIME (deprecated).
    Issues a deprecation warning if the old setting name is used.

    :return: Expiration time in seconds (default: DEFAULT_SECURITY_CODE_EXPIRATION_SECONDS)
    """
    phone_settings = getattr(django_settings, 'PHONE_VERIFICATION', {})

    # Check for new setting name first
    if 'SECURITY_CODE_EXPIRATION_SECONDS' in phone_settings:
        return phone_settings['SECURITY_CODE_EXPIRATION_SECONDS']

    # Fall back to old setting name with deprecation warning
    if 'SECURITY_CODE_EXPIRATION_TIME' in phone_settings:
        warnings.warn(
            "SECURITY_CODE_EXPIRATION_TIME is deprecated and will be removed in a future version. "
            "Please use SECURITY_CODE_EXPIRATION_SECONDS instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return phone_settings['SECURITY_CODE_EXPIRATION_TIME']

    # Default value
    return DEFAULT_SECURITY_CODE_EXPIRATION_SECONDS
