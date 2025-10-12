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


A Django app to support **phone number verification** using a security code sent via SMS.

``django-phone-verify`` provides a simple, secure way to verify phone numbers for user authentication, 2FA, account recovery, and more. It works seamlessly with Django and Django REST Framework, supports multiple SMS providers (Twilio, Nexmo/Vonage), and is fully extensible with custom backends.

📖 **Full Documentation:** `https://www.sanyamkhurana.com/django-phone-verify/ <https://www.sanyamkhurana.com/django-phone-verify/>`_

What It Does
------------

``django-phone-verify`` handles the complete phone verification flow:

1. **Send Verification Code** - User requests verification, receives SMS with security code
2. **Verify Code** - User submits code, system validates and confirms phone number
3. **Session Management** - Secure JWT-based session tokens prevent tampering
4. **Multiple Use Cases** - Registration, 2FA, password reset, marketing opt-in, and more

Key Features
------------

**Security & Flexibility**

- 🔐 **Secure verification flow** - JWT session tokens, configurable code expiration, one-time use options
- 🔧 **Highly customizable** - Token length, expiration time, message templates, custom backends
- 🔒 **Production-ready** - Rate limiting support, security best practices, GDPR/CCPA compliance guidance

**Easy Integration**

- 🚀 **Django REST Framework** - Pre-built viewsets and serializers for instant API setup
- 🔌 **Pluggable backends** - Use Twilio, Nexmo/Vonage, or write your own (AWS SNS, MessageBird, etc.)
- ✅ **Non-intrusive** - Works with any ``AUTH_USER_MODEL``, no database changes required to your user model
- 🧪 **Sandbox mode** - Test flows without sending real SMS messages

**Multiple Use Cases**

- 👤 User registration phone verification
- 🔑 Two-factor authentication (2FA)
- 🔄 Account recovery / password reset
- 📧 Marketing opt-in verification
- 📱 Phone number update flows

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

2. Run migrations:

.. code-block:: shell

    python manage.py migrate

3. Include the API URLs in your project's ``urls.py``:

.. code-block:: python

    from django.urls import path, include

    urlpatterns = [
        ...
        path("api/phone/", include("phone_verify.urls")),
        ...
    ]

4. Configure ``PHONE_VERIFICATION`` settings in your ``settings.py``:

**For Twilio:**

.. code-block:: python

    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.twilio.TwilioBackend",
        "OPTIONS": {
            "SID": "your-twilio-account-sid",
            "SECRET": "your-twilio-auth-token",
            "FROM": "+1234567890",  # Your Twilio phone number
            "SANDBOX_TOKEN": "123456",  # Optional: for testing without sending real SMS
        },
        "TOKEN_LENGTH": 6,
        "MESSAGE": "Welcome to {app}! Please use security code {security_code} to proceed.",
        "APP_NAME": "Phone Verify",
        "SECURITY_CODE_EXPIRATION_TIME": 3600,  # in seconds
        "VERIFY_SECURITY_CODE_ONLY_ONCE": False,
    }

**For Nexmo (Vonage):**

.. code-block:: python

    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.nexmo.NexmoBackend",
        "OPTIONS": {
            "KEY": "your-nexmo-api-key",
            "SECRET": "your-nexmo-api-secret",
            "FROM": "YourApp",  # Sender ID
            "SANDBOX_TOKEN": "123456",  # Optional: for testing
        },
        "TOKEN_LENGTH": 6,
        "MESSAGE": "Welcome to {app}! Please use security code {security_code} to proceed.",
        "APP_NAME": "Phone Verify",
        "SECURITY_CODE_EXPIRATION_TIME": 3600,
        "VERIFY_SECURITY_CODE_ONLY_ONCE": False,
    }

Quick Start
-----------

**Step 1: Send verification code**

.. code-block:: bash

    curl -X POST http://localhost:8000/api/phone/register/ \
      -H "Content-Type: application/json" \
      -d '{"phone_number": "+1234567890"}'

    # Response:
    # {
    #   "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    #   "phone_number": "+1234567890"
    # }

**Step 2: Verify the code**

.. code-block:: bash

    curl -X POST http://localhost:8000/api/phone/verify/ \
      -H "Content-Type: application/json" \
      -d '{
        "phone_number": "+1234567890",
        "security_code": "123456",
        "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
      }'

    # Response:
    # {
    #   "message": "Security code is valid",
    #   "phone_number": "+1234567890"
    # }

**Using in Python/Django code:**

.. code-block:: python

    from phone_verify.services import send_security_code_and_generate_session_token
    from phone_verify.services import verify_security_code

    # Send verification code via SMS
    session_token = send_security_code_and_generate_session_token(
        phone_number="+1234567890"
    )
    # User receives SMS: "Welcome to Phone Verify! Please use security code 847291 to proceed."

    # Verify the code user entered
    try:
        verify_security_code(
            phone_number="+1234567890",
            security_code="847291",
            session_token=session_token
        )
        print("✓ Phone number verified successfully!")
    except Exception as e:
        print(f"✗ Verification failed: {e}")

Documentation
-------------

Full documentation is available at `https://www.sanyamkhurana.com/django-phone-verify/ <https://www.sanyamkhurana.com/django-phone-verify/>`_

**Quick Links:**

- 📘 `Getting Started Guide <https://www.sanyamkhurana.com/django-phone-verify/getting_started.html>`_
- ⚙️ `Configuration Reference <https://www.sanyamkhurana.com/django-phone-verify/configuration.html>`_
- 🔌 `Integration Examples <https://www.sanyamkhurana.com/django-phone-verify/integration.html>`_
- 🚀 `Advanced Examples <https://www.sanyamkhurana.com/django-phone-verify/advanced_examples.html>`_ (2FA, password reset, marketing opt-in)
- 🔧 `Custom Backend Guide <https://www.sanyamkhurana.com/django-phone-verify/customization.html>`_
- 🔒 `Security Best Practices <https://www.sanyamkhurana.com/django-phone-verify/security.html>`_
- 📖 `API Reference <https://www.sanyamkhurana.com/django-phone-verify/api_reference.html>`_
- 🐛 `Troubleshooting Guide <https://www.sanyamkhurana.com/django-phone-verify/troubleshooting.html>`_

Compatibility
-------------

- Python 3.8+ (Python 3.7 and below are EOL)
- Django 2.1+
- Django REST Framework 3.9+

Contributing
------------

Found a bug? Want to suggest an improvement or submit a patch?

We welcome contributions! Here's how you can help:

1. 🐛 **Report bugs** via `GitHub Issues <https://github.com/CuriousLearner/django-phone-verify/issues>`_
2. 💡 **Suggest features** or improvements
3. 🔧 **Submit pull requests** - please check the `contributing guide <https://github.com/CuriousLearner/django-phone-verify/blob/master/docs/contributing.rst>`_ first
4. 📖 **Improve documentation**

Before submitting a PR:

- Write tests for new features
- Ensure all tests pass: ``pytest``
- Follow the existing code style
- Update documentation if needed

License
-------

This project is licensed under the **GPLv3** license.

Changelog
---------

See the full changelog here:
📄 `CHANGELOG.rst <https://github.com/CuriousLearner/django-phone-verify/blob/master/CHANGELOG.rst>`_
