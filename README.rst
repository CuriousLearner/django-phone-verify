django-phone-verify
===================

.. image:: https://github.com/CuriousLearner/django-phone-verify/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/CuriousLearner/django-phone-verify/actions/workflows/main.yml

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


``django-phone-verify`` is a Django app that enables simple phone number verification using a security code sent via SMS.
It supports Twilio and Nexmo (Vonage) out of the box and is fully customizable to suit your backend needs.

Docs are available at `https://www.sanyamkhurana.com/django-phone-verify/ <https://www.sanyamkhurana.com/django-phone-verify/>`_.

Features
--------

- 🔐 Verify phone numbers using SMS security codes
- 🔧 Supports custom token length and expiration time
- 🔄 Built-in support for Twilio and Nexmo (Vonage)
- 🧩 Easily extensible via pluggable backends
- ✅ Doesn't interfere with your existing ``AUTH_USER_MODEL``
- 🚀 Ready-to-use API endpoints via Django REST Framework
- 🛠 Can be used for multiple flows like signup, 2FA, marketing opt-in, etc.

Installation
------------

Install the package with all supported backends:

.. code-block:: shell

    pip install django-phone-verify[all]

Or install with just the backend you need:

.. code-block:: shell

    pip install django-phone-verify[twilio]
    pip install django-phone-verify[nexmo]

Configuration
-------------

1. Add ``phone_verify`` to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "phone_verify",
        ...
    ]

2. Configure ``PHONE_VERIFICATION`` settings:

.. code-block:: python

    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.twilio.TwilioBackend",  # or NexmoBackend
        "OPTIONS": {
            "SID": "fake",
            "SECRET": "fake",
            "FROM": "+14755292729",
            "SANDBOX_TOKEN": "123456",
        },
        "TOKEN_LENGTH": 6,
        "MESSAGE": "Welcome to {app}! Please use security code {security_code} to proceed.",
        "APP_NAME": "Phone Verify",
        "SECURITY_CODE_EXPIRATION_TIME": 3600,  # in seconds
        "VERIFY_SECURITY_CODE_ONLY_ONCE": False,
    }

**Note:** To use Nexmo instead of Twilio, change the ``BACKEND`` path to:

.. code-block:: python

    "BACKEND": "phone_verify.backends.nexmo.NexmoBackend"

and in ``OPTIONS``, use:

.. code-block:: python

    "KEY": "your-nexmo-key",
    "SECRET": "your-nexmo-secret"

Usage
-----

To get started using the app and integrating it into your own flow (DRF or non-DRF), check the following documentation:

- 📘 `Getting Started Guide <docs/getting_started.rst>`_
- 🔌 `Integration Examples <docs/integration.rst>`_
- ⚙️ `Custom Backend Guide <docs/customization.rst>`_
- 📮 `API Endpoints Reference <phone_verify/docs/api_endpoints.rst>`_

Compatibility
-------------

- Python 3.6+
- Django 2.1+
- Django REST Framework 3.9+

Contributing
------------

Found a bug? Want to suggest an improvement or submit a patch?
Pull requests are welcome! 🙌 Please check the `contributing guide <https://github.com/CuriousLearner/django-phone-verify/blob/master/docs/contributing.rst>`_ before you start.

License
-------

This project is licensed under the **GPLv3** license.

Changelog
---------

See the full changelog here:
📄 `CHANGELOG.rst <https://github.com/CuriousLearner/django-phone-verify/blob/master/CHANGELOG.rst>`_
