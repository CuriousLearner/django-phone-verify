# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

# Third Party Stuff
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# phone_verify stuff
from .backends import get_sms_backend

logger = logging.getLogger(__name__)

# iOS uses "session code" to parse the security code and support copying on clipboard.
DEFAULT_MESSAGE = (
    "Welcome to {app}, use session code {security_code} for authentication."
)
DEFAULT_APP_NAME = "Phone Verify"


class PhoneVerificationService(object):

    def __init__(self, phone_number, backend=None):
        try:
            self.phone_settings = settings.PHONE_VERIFICATION
        except AttributeError as e:
            raise ImproperlyConfigured("Please define PHONE_VERIFICATION in settings") from e
        self._check_required_settings()
        if backend is None:
            self.backend = get_sms_backend(phone_number=phone_number)
        else:
            self.backend = backend

        self.verification_message = self.phone_settings.get("MESSAGE", DEFAULT_MESSAGE)

    def send_verification(self, number, security_code, context=None):
        """
        Send a verification text to the given number to verify.

        :param number: the phone number of recipient.
        :param security_code: generated code to verify
        :param context: optional dictionary for custom message formatting
        """
        message = self._generate_message(security_code, context)
        self.backend.send_sms(number, message)

    def _generate_message(self, security_code, context=None):
        # If the backend has its own message generator, prefer it
        if hasattr(self.backend, "generate_message") and callable(self.backend.generate_message):
            message = self.backend.generate_message(security_code, context=context)
            if message:
                return message

        # Default fallback
        format_context = {
            "app": settings.PHONE_VERIFICATION.get("APP_NAME", DEFAULT_APP_NAME),
            "security_code": security_code,
        }
        if context:
            format_context.update(context)

        return self.verification_message.format(**format_context)

    def _check_required_settings(self):
        required_settings = {
            "BACKEND",
            "OPTIONS",
            "TOKEN_LENGTH",
            "MESSAGE",
            "APP_NAME",
            "SECURITY_CODE_EXPIRATION_TIME",
            "VERIFY_SECURITY_CODE_ONLY_ONCE",
        }
        user_settings = set(settings.PHONE_VERIFICATION.keys())
        if not required_settings.issubset(user_settings):
            raise ImproperlyConfigured(
                "Please specify following settings in settings.py: {}".format(
                    ", ".join(required_settings - user_settings)
                )
            )

        # Validate minimum token length
        token_length = settings.PHONE_VERIFICATION.get("TOKEN_LENGTH", 6)
        min_token_length = settings.PHONE_VERIFICATION.get("MIN_TOKEN_LENGTH", 6)
        if token_length < min_token_length:
            raise ImproperlyConfigured(
                f"TOKEN_LENGTH ({token_length}) cannot be less than MIN_TOKEN_LENGTH ({min_token_length})"
            )


def send_security_code_and_generate_session_token(phone_number):
    sms_backend = get_sms_backend(phone_number)
    security_code, session_token = sms_backend.create_security_code_and_session_token(
        phone_number
    )
    service = PhoneVerificationService(phone_number=phone_number)
    try:
        service.send_verification(phone_number, security_code)
    except service.backend.exception_class as exc:
        logger.error(
            "Error in sending verification code to {phone_number}: "
            "{error}".format(phone_number=phone_number, error=exc)
        )
    return session_token
