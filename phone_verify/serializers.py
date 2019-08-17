# -*- coding: utf-8 -*-

# Standard Library
import logging

# Third Party Stuff
from django.utils.translation import ugettext as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

# Phone Auth Stuff
from .backends import get_sms_backend

logger = logging.getLogger(__name__)


class PhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()


class SMSVerificationSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    session_code = serializers.CharField(required=True)
    security_code = serializers.CharField(required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        phone_number = attrs.get("phone_number", None)
        security_code, session_code = attrs.get("security_code", None), attrs.get("session_code", None)
        backend = get_sms_backend(phone_number=phone_number)
        verification, token_validatation = backend.validate_token(
            security_code=security_code, phone_number=phone_number
        )

        if verification is None:
            raise serializers.ValidationError(_("security_code is not valid"))
        elif not verification.session_code == session_code:
            raise serializers.ValidationError(_("Session Code mis-match"))
        elif token_validatation == backend.EXPIRED:
            raise serializers.ValidationError(_("security_code has expired"))
        return attrs
