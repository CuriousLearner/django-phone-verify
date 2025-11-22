# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Third Party Stuff
from django.contrib import admin

from .models import SMSVerification


@admin.register(SMSVerification)
class SMSVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "security_code",
        "phone_number",
        "is_verified",
        "is_valid",
        "failed_attempts",
        "created_at",
    )
    search_fields = ("phone_number",)
    ordering = ("phone_number",)
    list_filter = ("is_verified", "created_at")
    readonly_fields = (
        "security_code",
        "phone_number",
        "session_token",
        "is_verified",
        "is_valid",
        "failed_attempts",
        "created_at",
        "modified_at",
    )

    @admin.display(description="Is Valid", boolean=True)
    def is_valid(self, obj):
        """Display whether the security code is still valid (not expired)."""
        return not obj.is_expired
