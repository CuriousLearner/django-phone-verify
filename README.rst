django-phone-verify
===================

.. image:: https://github.com/github/docs/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/CuriousLearner/django-phone-verify/actions

.. image:: https://coveralls.io/repos/github/CuriousLearner/django-phone-verify/badge.svg?branch=master
    :target: https://coveralls.io/github/CuriousLearner/django-phone-verify?branch=master

.. image:: https://img.shields.io/pypi/l/django-phone-verify
    :target: https://pypi.python.org/pypi/django-phone-verify/
    :alt: License

.. image:: https://static.pepy.tech/badge/django-phone-verify?period=total&units=international_system&left_color=black&right_color=darkgreen&left_text=Downloads
   :target: https://pepy.tech/project/django-phone-verify

.. image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
   :target: https://www.python.org/

.. image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg
   :target: https://GitHub.com/CuriousLearner/django-phone-verify/graphs/commit-activity

.. image:: https://badge.fury.io/py/django-phone-verify.svg
   :target: https://pypi.python.org/pypi/django-phone-verify/

.. image:: https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square
   :target: http://makeapullrequest.com


A Django app to support phone number verification using the security code sent via SMS.

Salient Features
----------------

- Let's devs verify phone numbers via SMS.
- Extensibility to provide tokens with varying lengths.
- Comes with Twilio and Nexmo already integrated.
- Set expiration time on tokens.
- Provides an interface for writing custom SMS sending backend for easy extensibility.
- Does not mess up with existing ``AUTH_USER_MODEL`` at all.
- Can be used for several potential use-cases, and not just auth.
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
        ...
    ]

- Add settings for Phone Verify as you desire:

.. code-block:: python

    # In settings.py
    # Add settings for phone_verify to work
    PHONE_VERIFICATION = {
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
        "SECURITY_CODE_EXPIRATION_TIME": 3600,  # In seconds only
        "VERIFY_SECURITY_CODE_ONLY_ONCE": False,  # If False, then a security code can be used multiple times for verification
    }

Usage
-----

- To explore more about how to use, integrate and leverage the existing functionality of ``Django Phone Verify``, have a look at `getting_started.rst`_

.. _getting_started.rst: https://github.com/CuriousLearner/django-phone-verify/blob/master/docs/getting_started.rst

**Note**: ``Django Phone Verify`` also provides ``Nexmo`` as a backend service other than ``Twilio``. To switch to ``Nexmo``, replace ``BACKEND`` within your ``PHONE_VERIFICATION`` setting with ``phone_verify.backends.nexmo.NexmoBackend`` and define ``KEY`` within ``OPTIONS`` of ``PHONE_VERIFICATION`` setting, with your Nexmo API key, in place of already available ``SID``.

Compatibility
-------------
- Python 3.6+
- Django 2.1+
- Django REST Framework 3.9+

Contributing
------------

No code is bug-free and I'm sure this app will have bugs. If you find any bugs, please create an issue on GitHub.

Licence
-------

GPLv3

Changelog
---------

See `changelog.rst`_

.. _changelog.rst: https://github.com/CuriousLearner/django-phone-verify/blob/master/CHANGELOG.rst
