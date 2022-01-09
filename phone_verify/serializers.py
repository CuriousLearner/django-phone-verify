# -*- coding: utf-8 -*-

# Standard Library
import logging

# Third Party Stuff
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

# Phone Auth Stuff
from .backends import get_sms_backend

logger = logging.getLogger(__name__)


class PhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()


class SMSVerificationSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        phone_number = attrs.get("phone_number", None)
        security_code, session_token = (
            attrs.get("security_code", None),
            attrs.get("session_token", None),
        )
        backend = get_sms_backend(phone_number=phone_number)
        verification, token_validatation = backend.validate_security_code(
            security_code=security_code,
            phone_number=phone_number,
            session_token=session_token,
        )

        if verification is None:
            raise serializers.ValidationError(_("Security code is not valid"))
        elif token_validatation == backend.SESSION_TOKEN_INVALID:
            raise serializers.ValidationError(_("Session Token mis-match"))
        elif token_validatation == backend.SECURITY_CODE_EXPIRED:
            raise serializers.ValidationError(_("Security code has expired"))
        elif token_validatation == backend.SECURITY_CODE_VERIFIED:
            raise serializers.ValidationError(_("Security code is already verified"))

        return attrs
