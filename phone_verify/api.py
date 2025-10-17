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

        # Extract language from Accept-Language header
        # Format: "en-US,en;q=0.9,es;q=0.8" -> take first language "en-US"
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        language = None
        if accept_language:
            # Take first language, strip quality params (e.g., "en-US;q=0.9" -> "en-US")
            language = accept_language.split(',')[0].split(';')[0].strip() or None

        session_token = send_security_code_and_generate_session_token(
            str(serializer.validated_data["phone_number"]),
            language=language
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
