# -*- coding: utf-8 -*-

import random
from abc import ABCMeta, abstractmethod

# Third Party Stuff
import jwt
from django.conf import settings as django_settings
from django.utils import timezone
from django.utils.crypto import get_random_string

from ..models import SMSVerification

DEFAULT_TOKEN_LENGTH = 6


class BaseBackend(metaclass=ABCMeta):
    SECURITY_CODE_VALID = 0
    SECURITY_CODE_INVALID = 1
    SECURITY_CODE_EXPIRED = 2
    SECURITY_CODE_VERIFIED = 3
    SESSION_TOKEN_INVALID = 4

    def __init__(self, **settings):
        self.exception_class = None

    @abstractmethod
    def send_sms(self, number, message):
        raise NotImplementedError()

    @abstractmethod
    def send_bulk_sms(self, numbers, message):
        raise NotImplementedError()

    @classmethod
    def generate_security_code(cls):
        """
        Returns a unique random `security_code` for given `TOKEN_LENGTH` in the settings.
        """
        token_length = django_settings.PHONE_VERIFICATION.get(
            "TOKEN_LENGTH", DEFAULT_TOKEN_LENGTH
        )
        return get_random_string(token_length, allowed_chars="0123456789")

    @classmethod
    def generate_session_token(cls, phone_number):
        """
        Returns a unique session_token for
        identifying a particular device in subsequent calls.
        """
        data = {"phone_number": phone_number, "nonce": random.random()}
        session_token = jwt.encode(data, django_settings.SECRET_KEY)
        try:
            # PyJWT 2.0 returns a string instead of bytes
            # Bytes will always need a .decode() method.
            # We cannot upgrade to PyJWT 2.0.0 for now
            # since there is a dependency conflict with twilio.
            # TODO: Just return session_token when the other lib
            # versions are updated and we can pin PyJWT >= 2.0.0
            # More info: https://github.com/CuriousLearner/django-phone-verify/pull/57
            return session_token.decode()
        except AttributeError:
            return session_token

    @classmethod
    def check_security_code_expiry(cls, stored_verification):
        """
        Returns True if the `security_code` for the `stored_verification` is expired.
        """
        time_difference = timezone.now() - stored_verification.created_at
        if time_difference.seconds > django_settings.PHONE_VERIFICATION.get(
            "SECURITY_CODE_EXPIRATION_TIME"
        ):
            return True
        return False

    def create_security_code_and_session_token(self, number):
        """
        Creates a temporary `security_code` and `session_token` inside the DB.

        `security_code` is the code that user would enter to verify their phone_number.
        `session_token` is used to verify if the subsequent call for verification is
        by the same device that initiated a phone number verification in the
        first place.

        :param number: Phone number of recipient

        :return security_code: string of sha security_code
        :return session_token: string of session_token
        """
        security_code = self.generate_security_code()
        session_token = self.generate_session_token(number)

        # Delete old security_code(s) for phone_number if already exists
        SMSVerification.objects.filter(phone_number=number).delete()

        # Default security_code generated of 6 digits
        SMSVerification.objects.create(
            phone_number=number,
            security_code=security_code,
            session_token=session_token,
        )
        return security_code, session_token

    def validate_security_code(self, security_code, phone_number, session_token):
        """
        A utility method to verify if the `security_code` entered is valid for
        a given `phone_number` along with the `session_token` used.

        :param security_code: Security code entered for verification
        :param phone_number: Phone number to be verified
        :param session_token: Session token to identify the device

        :return stored_verification: Contains the verification object
        corresponding to the phone_number if found, else None.
        :return status: Status for the stored_verification object.
        Can be one of the following:
            - `BaseBackend.SECURITY_CODE_VALID`
            - `BaseBackend.SECURITY_CODE_INVALID`
            - `BaseBackend.SECURITY_CODE_EXPIRED`
            - `BaseBackend.SECURITY_CODE_VERIFIED`
            - `BaseBackend.SESSION_TOKEN_INVALID`
        """
        stored_verification = SMSVerification.objects.filter(
            security_code=security_code, phone_number=phone_number
        ).first()

        # check security_code exists
        if stored_verification is None:
            return stored_verification, self.SECURITY_CODE_INVALID

        # check session code exists
        if not stored_verification.session_token == session_token:
            return stored_verification, self.SESSION_TOKEN_INVALID

        # check security_code is not expired
        if self.check_security_code_expiry(stored_verification):
            return stored_verification, self.SECURITY_CODE_EXPIRED

        # check security_code is not verified
        if stored_verification.is_verified and django_settings.PHONE_VERIFICATION.get(
            "VERIFY_SECURITY_CODE_ONLY_ONCE"
        ):
            return stored_verification, self.SECURITY_CODE_VERIFIED

        # mark security_code as verified
        stored_verification.is_verified = True
        stored_verification.save()

        return stored_verification, self.SECURITY_CODE_VALID
