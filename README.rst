django-phone-verify
===================

.. image:: https://travis-ci.org/CuriousLearner/django-phone-verify.svg?branch=master
    :target: https://travis-ci.org/CuriousLearner/django-phone-verify

A Django app to support phone number verification using security code sent via SMS.

Salient Features
----------------

- Let's you verify phone numbers via SMS.
- Extensibility to provide different length of tokens.
- Comes with Twilio already integrated.
- Set expiration time on tokens.
- Provides interface for writing custom SMS sending backend for easy extensibility.
- Does not mess-up with existing ``AUTH_USER_MODEL`` at all.
- Can be used for a number of potential cases, and not just auth.
- Provides ready endpoints for sending SMS and verification (See `api_endpoints.rst`_).

.. _api_endpoints.rst: https://github.com/CuriousLearner/django-phone-verify/blob/master/phone_verify/docs/api_endpoints.rst

Installation
------------

.. code-block:: shell

    pip install django-phone-verify

Configuration
-------------

- Add app to `INSTALLED_APPS`

.. code-block:: python

    # In settings.py:

    # Add app to `INSTALLED_APPS`
    INSTALLED_APPS = [
        ...
        "phone_verify",
    ]

- Add settings for Phone Verify as you desire:

.. code-block:: python

    # In settings.py
    # Add settings for phone_verify to work
    "PHONE_VERIFICATION" = {
        "BACKEND": "phone_verify.backends.twilio.TwilioBackend",
        "TWILIO_SANDBOX_TOKEN": "123456",
        "OPTIONS": {
            "SID": "fake",
            "SECRET": "fake",
            "FROM": "+14755292729"
        },
        "TOKEN_LENGTH": 6,
        "MESSAGE": "Welcome to {app}! Please use security code {security_code} to proceed.",
        "APP_NAME": "Phone Verify",
        "SECURITY_CODE_EXPIRATION_TIME": 3600,  # In seconds only
        "VERIFY_SECURITY_CODE_ONLY_ONCE": False,  # If False, then a security code can be used multiple times for verification
    },

Usage
-----

- To explore more about how to use, integrate and leverage existing functionality of `Django Phone Verify`, have a look at `usage.rst`_

.. _usage.rst: https://github.com/CuriousLearner/django-phone-verify/blob/master/docs/usage.rst

Compatibility
-------------
- Django 2.1+
- Django REST Framework 3.9+

Licence
-------

GPLv3
