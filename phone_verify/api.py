# -*- coding: utf-8 -*-

# Third Party Stuff
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import PhoneSerializer, SMSVerificationSerializer
from .services import send_security_code_and_generate_session_token


def _preferred_language(accept_language):
    """Return the highest priority language of an ``Accept-Language`` header.

    Entries are ranked by their ``q`` weight (RFC 7231), defaulting to 1.0 when
    absent. A weight of 0 means "not acceptable", so those entries are dropped.
    Ties keep the order they appear in the header, and malformed entries are
    ignored. Returns ``None`` when the header carries no usable language, so
    that the message is sent unlocalized.
    """
    candidates = []
    for entry in accept_language.split(","):
        language, _, params = entry.strip().partition(";")
        language = language.strip()
        if not language:
            continue
        weight = 1.0
        if params:
            key, _, value = params.partition("=")
            if key.strip().lower() != "q":
                continue
            try:
                weight = float(value)
            except ValueError:
                continue
        if weight <= 0:
            continue
        candidates.append((language, weight))

    # `sort` is stable, so entries of equal weight keep their header order.
    candidates.sort(key=lambda candidate: candidate[1], reverse=True)
    return candidates[0][0] if candidates else None


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

        language = _preferred_language(request.META.get("HTTP_ACCEPT_LANGUAGE", ""))

        session_token = send_security_code_and_generate_session_token(
            str(serializer.validated_data["phone_number"]),
            language=language
        )
        return Response({"session_token": session_token})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=SMSVerificationSerializer,
    )
    def verify(self, request):
        serializer = SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Security code is valid."})
