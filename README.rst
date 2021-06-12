django-phone-verify
===================

.. image:: https://travis-ci.org/CuriousLearner/django-phone-verify.svg?branch=master
    :target: https://travis-ci.org/CuriousLearner/django-phone-verify

.. image:: https://coveralls.io/repos/github/CuriousLearner/django-phone-verify/badge.svg?branch=master
    :target: https://coveralls.io/github/CuriousLearner/django-phone-verify?branch=master

.. image:: https://pypip.in/license/django-phone-verify/badge.svg
    :target: https://pypi.python.org/pypi/django-phone-verify/
    :alt: License

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
- Comes with Twilio already integrated.
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

- To explore more about how to use, integrate and leverage the existing functionality of ``Django Phone Verify``, have a look at `usage.rst`_

.. _usage.rst: https://github.com/CuriousLearner/django-phone-verify/blob/master/docs/usage.rst

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

Release Notes
-------------

[Dev]
^^^^^

Added
"""""
- Support for Django 3.2.

Changed
"""""""
- Method ``phone_verify.backends.nexmo.NexmoBackend.send_sms`` changes parameter name from ``numbers`` to ``number`` to be consistent with rest of the inherited classes.

[2.0.1]
^^^^^^^

Added
"""""
- Support for Python 3.8 & Python 3.9.
- CI tests for Py{36,37,38,39}-Django{20,21,22,30,31}.

Changed
"""""""
- Fixed issue ``generate_session_token`` to handle cases in Py38, Py39 when the ``session_token`` is already ``string`` instead of ``bytes``.

[2.0.0]
^^^^^^^

**NOTE**: The previous version of this library provided the ``security_code`` in the JWT ``session_token``. You would have to re-verify ``phone_numbers`` in *this* version to ensure they are authentically verified.

Added
"""""

- Tests added to provide 100% coverage on the package.
- Add ``nexmo.errors.ClientError`` as exception class in ``phone_verify.backends.nexmo.NexmoBackend`` & ``phone_verify.backends.nexmo.NexmoSandboxBackend``.

Changed
"""""""

- Method signature changed for ``phone_verify.backends.BaseBackend.generate_session_token``. It now accepts only ``phone_number`` instead of combination of ``phone_number`` and ``security_code``.
- Remove the ``security_code`` from JWT ``session_token`` to avoid leaking information.
- Add nonce in ``session_token`` to generate unique tokens for each ``phone_number``.
- Fixes call to ``phone_verify.backends.nexmo.NexmoBackend.send_sms`` method.

[1.1.0]
^^^^^^^

Added
"""""

- Support ``Nexmo`` as a backend service along with ``Twilio``.
- Add docs for writing a custom backend.

Changed
"""""""

- Update ``backends.base.BaseBackend.validate_security_code`` to use ``save()`` instead of ``update()`` to allow Django to emit its ``post_save()`` signal.

[1.0.0]
^^^^^^^

Added
"""""

- Add coverage report through ``coveralls``.
- Support for One-Time Passwords (OTP) using ``VERIFY_SECURITY_CODE_ONLY_ONCE`` as ``True`` in the settings.
- Script to support makemigrations for development.
- ``BaseBackend`` status now have ``SECURITY_CODE_VERIFIED`` and ``SESSION_TOKEN_INVALID`` status to support new states.

Changed
"""""""

- Rename ``TWILIO_SANDBOX_TOKEN`` to ``SANDBOX_TOKEN``.
- Fix signature for ``send_bulk_sms`` method in ``TwilioBackend`` and ``TwilioSandboxBackend``.
- Response for ``/api/phone/register`` contains key ``session_token`` instead of ``session_code``.
- Request payload for ``/api/phone/verify`` now expects ``session_token`` key instead of ``session_code``.
- Response for ``/api/phone/verify`` now sends additional response of ``Security code is already verified`` in case ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is set to ``True``.
- Rename ``otp`` to ``security_code`` in code and docs to be more consistent.
- Rename ``BaseBackend`` status from ``VALID``, ``INVALID``, ``EXPIRED`` to ``SECURITY_CODE_VALID``, ``SECURITY_CODE_INVALID``, and ``SECURITY_CODE_EXPIRED`` respectively.
- Rename ``session_code`` to ``session_token`` to be consistent in code and naming across the app.
- Rename service ``send_otp_and_generate_session_code`` to ``send_security_code_and_generate_session_token``.
- Rename method ``BaseBackend.generate_token`` to ``BaseBackend.generate_security_code``.
- Rename method ``create_otp_and_session_token`` to ``create_security_code_and_session_token``.
- Rename method ``BaseBackend.validate_token`` to ``BaseBackend.validate_security_code`` with an additional parameter of ``session_token``.

[0.2.0]
^^^^^^^

Added
"""""

- ``pre-commit-config`` to maintain code quality using black and other useful tools.
- Docs for integration and usage in `usage.rst`_.
- Tox for testing on `py{37}-django{20,21,22}`.
- Travis CI for testing builds.

Changed
"""""""

- Convert ``*.md`` docs to reST Markup.
- Fix issue with installing required package dependencies via ``install_requires``.

[0.1.1]
^^^^^^^

Added
"""""

- README and documentation of API endpoints.
- ``setup.cfg`` to manage coverage.
- ``phone_verify`` app including backends, requirements, tests.
- Initial app setup.
