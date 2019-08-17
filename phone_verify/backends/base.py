# -*- coding: utf-8 -*-

# Third Party Stuff
import jwt
from django.conf import settings as django_settings
from django.utils import timezone
from django.utils.crypto import get_random_string

from ..models import SMSVerification

DEFAULT_TOKEN_LENGTH = 6


class BaseBackend(object):
    SECURITY_CODE_VALID = 0
    SECURITY_CODE_INVALID = 1
    SECURITY_CODE_EXPIRED = 2
    SECURITY_CODE_VERIFIED = 3
    SESSION_CODE_INVALID = 4

    def __init__(self, **settings):
        self.exception_class = None

    def send_sms(self, numbers, message):
        raise NotImplementedError()

    def send_bulk_sms(self, numbers, message):
        raise NotImplementedError()

    @classmethod
    def generate_token(cls):
        """
        Returns an unique random token
        """
        token_length = django_settings.PHONE_VERIFICATION.get(
            "TOKEN_LENGTH", DEFAULT_TOKEN_LENGTH
        )
        return get_random_string(token_length, allowed_chars="0123456789")

    @classmethod
    def generate_session_token(cls, token, phone_number):
        """
        Returns an unique random token for a particular device
        """
        data = {"device_%s_session_code" % phone_number: token}
        return jwt.encode(data, django_settings.SECRET_KEY).decode()

    @classmethod
    def token_expired(cls, stored_verification):
        time_difference = timezone.now() - stored_verification.created_at
        if time_difference.seconds > django_settings.PHONE_VERIFICATION.get(
            "SECURITY_CODE_EXPIRATION_TIME"
        ):
            return True
        return False

    def create_security_code_and_session_token(self, number):
        """
        Creates a temporary security_code inside the cache, this holds the phone number
        as value, so that we can later check if everything is correct.

        It also generates a session_code for the client to send in subsequent requests.

        :param number: Number of recipient

        :return security_code: string of sha security_code
        :return session_code: string of session_code
        """
        security_code = self.generate_token()
        session_code = self.generate_session_token(security_code, number)

        # Delete old security_code(s) for phone_number if already exists
        SMSVerification.objects.filter(phone_number=number).delete()

        # Default security_code generated of 6 digits
        SMSVerification.objects.create(
            phone_number=number, security_code=security_code, session_code=session_code, is_verified=False
        )
        return security_code, session_code

    def validate_token(self, security_code, phone_number, session_code):
        stored_verification = SMSVerification.objects.filter(
            security_code=security_code, phone_number=phone_number
        ).first()

        # check security_code exists
        if stored_verification is None:
            return stored_verification, self.SECURITY_CODE_INVALID

        # check session code exists
        if not stored_verification.session_code == session_code:
            return stored_verification, self.SESSION_CODE_INVALID

        # check security_code is not expired
        if self.token_expired(stored_verification):
            return stored_verification, self.SECURITY_CODE_EXPIRED

        # check security_code is not verified
        if stored_verification.is_verified and django_settings.PHONE_VERIFICATION.get(
            "VERIFY_SECURITY_CODE_ONLY_ONCE"
        ):
            return stored_verification, self.SECURITY_CODE_VERIFIED

        # mark security_code as verified
        stored_verification = SMSVerification.objects.filter(
            security_code=security_code, phone_number=phone_number, session_code=session_code
        ).update(is_verified=True)

        return stored_verification, self.SECURITY_CODE_VALID
