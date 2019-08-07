# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Third Party Stuff
from django.contrib import admin

from .models import SMSVerification


@admin.register(SMSVerification)
class SMSVerificationAdmin(admin.ModelAdmin):
    list_display = ("id", "otp", "phone_number", "created_at")
    search_fields = ("phone_number",)
    ordering = ("phone_number",)
    readonly_fields = (
        "otp",
        "phone_number",
        "session_code",
        "created_at",
        "modified_at",
    )
