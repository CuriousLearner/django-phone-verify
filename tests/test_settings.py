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
        "TWILIO_SANDBOX_TOKEN": "123456",
        "OPTIONS": {"SID": "fake", "SECRET": "fake", "FROM": "+14755292729"},
        "TOKEN_LENGTH": 6,
        "MESSAGE": "Welcome to {app}! Please use security code {otp} to proceed.",
        "APP_NAME": "Phone Verify",
        "OTP_EXPIRATION_TIME": 1,  # In seconds only
    },
}
