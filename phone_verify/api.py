# -*- coding: utf-8 -*-

# Third Party Stuff
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .base import response
from .serializers import PhoneSerializer, SMSVerificationSerializer
from .services import send_otp_and_generate_session_code


class VerificationViewSet(viewsets.GenericViewSet):
    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=PhoneSerializer,
    )
    def register(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_code = send_otp_and_generate_session_code(
            str(serializer.validated_data["phone_number"])
        )
        return response.Ok({"session_code": session_code})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=SMSVerificationSerializer,
    )
    def verify(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Ok({"message": "OTP is valid."})
