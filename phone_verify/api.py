# -*- coding: utf-8 -*-

# Third Party Stuff
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .base import response
from .serializers import PhoneSerializer, SMSVerificationSerializer
from .services import send_security_code_and_generate_session_token


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
        session_token = send_security_code_and_generate_session_token(
            str(serializer.validated_data["phone_number"])
        )
        return response.Ok({"session_token": session_token})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=SMSVerificationSerializer,
    )
    def verify(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Ok({"message": "Security code is valid."})
