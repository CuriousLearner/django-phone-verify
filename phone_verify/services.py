# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

# Third Party Stuff
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# phone_verify stuff
from .backends import get_sms_backend


logger = logging.getLogger(__name__)

# iOS uses "session code" to parse the OTP and support copying on clipboard.
DEFAULT_MESSAGE = "Welcome to {app}, use session code {otp} for authentication."
DEFAULT_APP_NAME = 'Phone Verify'


class PhoneVerificationService(object):
    try:
        phone_settings = settings.PHONE_VERIFICATION
    except AttributeError:
        raise ImproperlyConfigured('Please define PHONE_VERIFICATION in settings')

    verification_message = phone_settings.get('MESSAGE', DEFAULT_MESSAGE)

    def __init__(self, phone_number, backend=None):
        if backend is None:
            self.backend = get_sms_backend(phone_number=phone_number)

    def send_verification(self, number, otp):
        """
        Send a verification text to the given number to verify.

        :param number: the phone number of recipient.
        """
        message = self._generate_message(otp)

        self.backend.send_sms(number, message)

    def _generate_message(self, otp):
        return self.verification_message.format(
            app=settings.PHONE_VERIFICATION.get('APP_NAME', DEFAULT_APP_NAME),
            otp=otp
        )


def send_otp_and_generate_session_code(phone_number):
    sms_backend = get_sms_backend(phone_number)
    otp, session_code = sms_backend.create_otp_and_session_token(phone_number)
    service = PhoneVerificationService(phone_number=phone_number)
    try:
        service.send_verification(phone_number, otp)
    except service.backend.exception_class as exc:
        logger.error('Error in sending verification code to {phone_number}: '
                     '{error}'.format(phone_number=phone_number, error=exc))
    return session_code
