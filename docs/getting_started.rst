Getting Started
===============

This guide will walk you through installing and configuring ``django-phone-verify`` in your Django project.
By the end, you'll have a working phone verification system ready to use.

Prerequisites
-------------

Before you begin, make sure you have:

- **Python 3.8+** installed
- **Django 2.1+** in your project
- **Django REST Framework 3.9+** (if using the API viewsets)
- An account with **Twilio** or **Nexmo/Vonage** (for sending SMS in production)

Installation
------------

You can install ``django-phone-verify`` using ``pip``. The package supports optional extras
for different SMS backends:

.. code-block:: shell

    # Install with Twilio support (recommended for most users)
    pip install django-phone-verify[twilio]

    # Or install with Nexmo/Vonage support
    pip install django-phone-verify[nexmo]

    # Install with all supported backends
    pip install django-phone-verify[all]

    # Core only (if you're writing a custom backend)
    pip install django-phone-verify

.. note::
    We recommend installing with ``[twilio]`` or ``[nexmo]`` extras to ensure all required
    dependencies are installed for your chosen SMS provider.


Configuration
-------------

Follow these steps to configure ``django-phone-verify`` in your Django project:

Step 1: Add to INSTALLED_APPS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add ``phone_verify`` to your ``INSTALLED_APPS`` in ``settings.py``:

.. code-block:: python

    # settings.py

    INSTALLED_APPS = [
        ...
        'phone_verify',
        ...
    ]

Step 2: Run Migrations
^^^^^^^^^^^^^^^^^^^^^^

Create the necessary database tables:

.. code-block:: shell

    python manage.py migrate

This creates the ``SMSVerification`` table to store phone numbers, session tokens, and security codes.

Step 3: Add URLs (if using DRF API)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Include the phone verification URLs in your project's ``urls.py``:

.. code-block:: python

    # urls.py
    from django.urls import path, include

    urlpatterns = [
        ...
        path('api/phone/', include('phone_verify.urls')),
        ...
    ]

This provides the ``/api/phone/register/`` and ``/api/phone/verify/`` endpoints.

Step 4: Configure PHONE_VERIFICATION Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the ``PHONE_VERIFICATION`` configuration to your ``settings.py``.

**For Twilio:**

.. code-block:: python

    # settings.py
    import os

    PHONE_VERIFICATION = {
        'BACKEND': 'phone_verify.backends.twilio.TwilioBackend',
        'OPTIONS': {
            'SID': os.environ.get('TWILIO_ACCOUNT_SID'),      # Your Twilio Account SID
            'SECRET': os.environ.get('TWILIO_AUTH_TOKEN'),    # Your Twilio Auth Token
            'FROM': os.environ.get('TWILIO_PHONE_NUMBER'),    # Your Twilio phone number (e.g., '+1234567890')
        },
        'TOKEN_LENGTH': 6,                                     # Length of security code
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'MyApp',                                   # Your app name (used in MESSAGE)
        'SECURITY_CODE_EXPIRATION_TIME': 600,                 # 10 minutes (in seconds)
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,               # Code can only be used once
    }

**For Nexmo/Vonage:**

.. code-block:: python

    # settings.py
    import os

    PHONE_VERIFICATION = {
        'BACKEND': 'phone_verify.backends.nexmo.NexmoBackend',
        'OPTIONS': {
            'KEY': os.environ.get('NEXMO_API_KEY'),           # Your Nexmo API Key
            'SECRET': os.environ.get('NEXMO_API_SECRET'),     # Your Nexmo API Secret
            'FROM': 'MyApp',                                   # Sender ID (alphanumeric or phone number)
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'MyApp',
        'SECURITY_CODE_EXPIRATION_TIME': 600,
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,
    }

.. important::
    **Security Best Practice**: Never hardcode credentials in your settings file. Use environment
    variables or a secrets management system. See :doc:`security` for more details.

Step 5: Set Up Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a ``.env`` file in your project root (and add it to ``.gitignore``):

.. code-block:: bash

    # .env (for Twilio)
    TWILIO_ACCOUNT_SID=your_account_sid_here
    TWILIO_AUTH_TOKEN=your_auth_token_here
    TWILIO_PHONE_NUMBER=+1234567890

Load environment variables in your ``settings.py``:

.. code-block:: python

    # settings.py
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file

Configuration Options Explained
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here's what each setting does:

- **BACKEND**: The SMS backend class to use (Twilio, Nexmo, or custom)
- **OPTIONS**: Provider-specific credentials and settings

  - Twilio: ``SID``, ``SECRET``, ``FROM``
  - Nexmo: ``KEY``, ``SECRET``, ``FROM``

- **TOKEN_LENGTH**: Number of digits in the security code (recommended: 6)
- **MESSAGE**: SMS message template. Variables: ``{app}`` and ``{security_code}``
- **APP_NAME**: Your application name (used in MESSAGE template)
- **SECURITY_CODE_EXPIRATION_TIME**: How long codes are valid (in seconds). Recommended: 300-600 (5-10 minutes)
- **VERIFY_SECURITY_CODE_ONLY_ONCE**: If ``True``, codes can only be used once

For detailed configuration options, see the :doc:`configuration` reference.


Testing Your Setup
------------------

You can quickly test if everything is working using the Django shell:

.. code-block:: python

    python manage.py shell

    >>> from phone_verify.services import send_security_code_and_generate_session_token
    >>> from phone_verify.services import verify_security_code
    >>>
    >>> # Send verification code
    >>> phone = "+1234567890"  # Use your real phone number for testing
    >>> session_token = send_security_code_and_generate_session_token(phone)
    >>> print(f"Session token: {session_token}")
    >>>
    >>> # Check your phone for the SMS, then verify
    >>> code = "123456"  # Enter the code you received
    >>> verify_security_code(phone, code, session_token)
    (<QuerySet []>, 'SECURITY_CODE_VALID')

If you see ``'SECURITY_CODE_VALID'``, congratulations! Your setup is working correctly.

.. tip::
    **Testing Without Real SMS**: To test without sending actual SMS messages, use a sandbox backend.
    See :doc:`customization` for how to create a sandbox backend that returns a fixed code.

Next Steps
----------

Now that you have ``django-phone-verify`` installed and configured, you can:

1. **Integrate into your app** - See :doc:`integration` for examples of integrating phone verification into user registration, login, etc.
2. **Explore advanced use cases** - Check out :doc:`advanced_examples` for 2FA, password reset, and more
3. **Customize the backend** - Write your own SMS backend in :doc:`customization`
4. **Secure your implementation** - Review :doc:`security` for production best practices
5. **Troubleshoot issues** - Visit :doc:`troubleshooting` if you encounter any problems
