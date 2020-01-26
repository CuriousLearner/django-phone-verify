DJANGO_SETTINGS = {
    "SECRET_KEY": "change-me-later",
    "DATABASES": {"default": {"ENGINE": "django.db.backends.sqlite3"}},
    "ROOT_URLCONF": "phone_verify.urls",
    "INSTALLED_APPS": [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "phone_verify",
    ],
    # PHONE VERIFICATION
    "PHONE_VERIFICATION": {
        "BACKEND": "phone_verify.backends.twilio.TwilioBackend",
        "OPTIONS": {
            "SID": "fake",
            "SECRET": "fake",
            "FROM": "+14755292729",
            "SANDBOX_TOKEN": "123456",
        },
        "TOKEN_LENGTH": 6,
        "MESSAGE": "Welcome to {app}! Please use security code {security_code} to proceed.",
        "APP_NAME": "Phone Verify",
        "SECURITY_CODE_EXPIRATION_TIME": 1,  # In seconds only
        "VERIFY_SECURITY_CODE_ONLY_ONCE": False,
    },
}
