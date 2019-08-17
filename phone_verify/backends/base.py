# -*- coding: utf-8 -*-

# Third Party Stuff
import jwt
from django.conf import settings as django_settings
from django.utils import timezone
from django.utils.crypto import get_random_string

from ..models import SMSVerification

DEFAULT_TOKEN_LENGTH = 6


class BaseBackend(object):
    OTP_VALID = 0
    OTP_INVALID = 1
    OTP_EXPIRED = 2
    OTP_VERIFIED = 3
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
            "OTP_EXPIRATION_TIME"
        ):
            return True
        return False

    def create_otp_and_session_token(self, number):
        """
        Creates a temporary otp (OTP) inside the cache, this holds the phone number
        as value, so that we can later check if everything is correct.

        It also generates a session_code for the client to send in subsequent requests.

        :param number: Number of recipient

        :return otp: string of sha otp
        :return session_code: string of session_code
        """
        otp = self.generate_token()
        session_code = self.generate_session_token(otp, number)

        # Delete old OTPs for phone_number if already exists
        SMSVerification.objects.filter(phone_number=number).delete()

        # Default otp generated of 6 digits
        SMSVerification.objects.create(
            phone_number=number, otp=otp, session_code=session_code, is_verified=False
        )
        return otp, session_code

    def validate_token(self, otp, phone_number, session_code):
        stored_verification = SMSVerification.objects.filter(
            otp=otp, phone_number=phone_number
        ).first()

        # check otp exists
        if stored_verification is None:
            return stored_verification, self.OTP_INVALID

        # check session code exists
        if not stored_verification.session_code == session_code:
            return stored_verification, self.SESSION_CODE_INVALID

        # check otp is not expired
        if self.token_expired(stored_verification):
            return stored_verification, self.OTP_EXPIRED

        # check otp is not verified
        if stored_verification.is_verified and django_settings.PHONE_VERIFICATION.get(
            "VERIFY_OTP_ONLY_ONCE"
        ):
            return stored_verification, self.OTP_VERIFIED

        # mark otp as verified
        stored_verification = SMSVerification.objects.filter(
            otp=otp, phone_number=phone_number, session_code=session_code
        ).update(is_verified=True)

        return stored_verification, self.OTP_VALID
