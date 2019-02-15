
SECRET_KEY = "change-me-later",
DEBUG = True,
USE_TZ = True,
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}
ROOT_URLCONF = "phone_verify.urls",
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "phone_verify",
]
# PHONE VERIFICATION
PHONE_VERIFICATION = {
    'BACKEND': 'phone_verify.backends.twilio.TwilioBackend',
    'TWILIO_SANDBOX_TOKEN':'123456',
    'OPTIONS': {
        'SID': 'fake',
        'SECRET': 'fake',
        'FROM': '+14755292729'
    },
    'TOKEN_LENGTH': 6,
    'MESSAGE': 'Welcome to {app}! Please use security code {otp} to proceed.',
    'APP_NAME': 'FAKE',
    'APP_BASE_URL': 'fake://',
    'APP_PATH': 'verify',
    'OTP_EXPIRATION_TIME': 3600  # In seconds only
}
