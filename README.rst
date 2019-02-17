django-phone-verify
===================

A Django app to support phone number verification using security code / One-Time-Password (OTP) sent via SMS.

Salient Features
----------------

- Let's you verify phone numbers via SMS.
- Extensibility to provide different length of tokens.
- Comes with Twilio already integrated.
- Set expiration time on tokens.
- Provides interface for writing custom SMS sending backend for easy extensibility.
- Does not mess-up with existing `AUTH_USER_MODEL` at all.
- Can be used for a number of potential cases, and not just auth.
- Provides ready endpoints for sending SMS and verification.

Installation
------------

.. code::

    pip install django-phone-verify

Usage
-----

- Add app to `INSTALLED_APPS`

    .. code::

        # In settings.py:

        # Add app to `INSTALLED_APPS`
        INSTALLED_APPS = [
            ...
            'phone_verify',
        ]

- Add settings for Phone Verify as you desire:

    .. code ::

        # Add settings for phone_verify to work
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
            'APP_NAME': 'Phone Verify',
            'OTP_EXPIRATION_TIME': 3600  # In seconds only
        }

Compatibility
-------------
- Django 2.1+
- Django REST Framework 3.9+

Licence
-------

GPLv3
