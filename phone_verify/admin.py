# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Third Party Stuff
from django.contrib import admin

from .models import SMSVerification


@admin.register(SMSVerification)
class SMSVerificationAdmin(admin.ModelAdmin):
    list_display = ("id", "security_code", "phone_number", "is_verified", "created_at")
    search_fields = ("phone_number",)
    ordering = ("phone_number",)
    readonly_fields = (
        "security_code",
        "phone_number",
        "session_token",
        "is_verified",
        "created_at",
        "modified_at",
    )
