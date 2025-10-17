.. _configuration:

Configuration Reference
=======================

This page provides detailed documentation for all configuration options available in ``django-phone-verify``.

Overview
--------

All configuration is defined in a single dictionary called ``PHONE_VERIFICATION`` in your Django ``settings.py``:

.. code-block:: python

    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.twilio.TwilioBackend",
        "OPTIONS": {...},
        "TOKEN_LENGTH": 6,
        "MESSAGE": "Your code is {security_code}",
        "APP_NAME": "MyApp",
        "SECURITY_CODE_EXPIRATION_TIME": 3600,
        "VERIFY_SECURITY_CODE_ONLY_ONCE": False,
    }

Required Settings
-----------------

BACKEND
^^^^^^^

**Type:** ``str``

**Required:** Yes

The Python import path to the SMS backend class.

**Built-in Options:**

- ``"phone_verify.backends.twilio.TwilioBackend"`` - Production Twilio backend
- ``"phone_verify.backends.twilio.TwilioSandboxBackend"`` - Twilio sandbox for testing
- ``"phone_verify.backends.nexmo.NexmoBackend"`` - Production Nexmo/Vonage backend
- ``"phone_verify.backends.nexmo.NexmoSandboxBackend"`` - Nexmo sandbox for testing

**Custom Backend:**

.. code-block:: python

    "BACKEND": "myapp.backends.CustomSMSBackend"

See :doc:`customization` for details on creating custom backends.

OPTIONS
^^^^^^^

**Type:** ``dict``

**Required:** Yes

Backend-specific configuration options. The keys and values depend on which backend you're using.

**For TwilioBackend:**

.. code-block:: python

    "OPTIONS": {
        "SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",     # Twilio Account SID
        "SECRET": "your_auth_token",                      # Twilio Auth Token
        "FROM": "+15551234567",                           # Your Twilio phone number (E.164)
        "SANDBOX_TOKEN": "123456",                        # Optional: fixed token for sandbox
    }

- ``SID``: Found in your Twilio console
- ``SECRET``: Your Twilio Auth Token
- ``FROM``: Must be a Twilio phone number you own
- ``SANDBOX_TOKEN``: Only used by ``TwilioSandboxBackend``

**For NexmoBackend:**

.. code-block:: python

    "OPTIONS": {
        "KEY": "your_api_key",        # Nexmo API Key
        "SECRET": "your_api_secret",  # Nexmo API Secret
        "FROM": "YourApp",            # Sender ID (alphanumeric) or phone number
        "SANDBOX_TOKEN": "123456",    # Optional: fixed token for sandbox
    }

- ``KEY``: Your Nexmo API key
- ``SECRET``: Your Nexmo API secret
- ``FROM``: Can be alphanumeric (e.g., "MyApp") or a phone number
- ``SANDBOX_TOKEN``: Only used by ``NexmoSandboxBackend``

**For Custom Backends:**

Define whatever keys your custom backend needs. These are passed to the backend's ``__init__`` method.

TOKEN_LENGTH
^^^^^^^^^^^^

**Type:** ``int``

**Required:** Yes

**Default:** 6 (when using ``BaseBackend.generate_security_code()``)

The length of the numeric security code to generate.

.. code-block:: python

    "TOKEN_LENGTH": 6  # Generates codes like "123456"
    "TOKEN_LENGTH": 4  # Generates codes like "5738"

**Recommendations:**

- **4 digits**: Easier for users to type, but less secure (10,000 combinations)
- **6 digits**: Standard for most apps (1,000,000 combinations)
- **8+ digits**: More secure but harder to remember

.. note::
   This setting only affects the default ``generate_security_code()`` method. Custom backends can override this method to use different formats (alphanumeric, etc.).

MESSAGE
^^^^^^^

**Type:** ``str``

**Required:** Yes

The SMS message template. Supports placeholders:

- ``{security_code}`` - The generated verification code
- ``{app}`` - The value of ``APP_NAME`` setting
- Any keys from the ``context`` dict passed to ``send_verification()``

**Examples:**

.. code-block:: python

    # Simple message
    "MESSAGE": "Your verification code is {security_code}"

    # With app name
    "MESSAGE": "Welcome to {app}! Your code is {security_code}"

    # iOS-friendly (for auto-parsing)
    "MESSAGE": "Your {app} verification code is {security_code}"

    # Custom context (if you pass context={'username': 'Alice'})
    "MESSAGE": "Hi {username}, your {app} code is {security_code}"

.. tip::
   For iOS auto-fill to work, the message should contain the word "code" followed by the actual code.

.. note::
   If your backend implements ``generate_message(security_code, context=None)``, that method takes precedence over this setting.

APP_NAME
^^^^^^^^

**Type:** ``str``

**Required:** Yes

The name of your application, used in the ``MESSAGE`` template.

.. code-block:: python

    "APP_NAME": "MyApp"
    "APP_NAME": "Acme Corp"

This value is available as ``{app}`` in the message template.

SECURITY_CODE_EXPIRATION_TIME
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Type:** ``int`` (seconds)

**Required:** Yes

How long a security code remains valid after being generated.

.. code-block:: python

    "SECURITY_CODE_EXPIRATION_TIME": 300     # 5 minutes
    "SECURITY_CODE_EXPIRATION_TIME": 600     # 10 minutes
    "SECURITY_CODE_EXPIRATION_TIME": 1800    # 30 minutes
    "SECURITY_CODE_EXPIRATION_TIME": 3600    # 1 hour

**Recommendations:**

- **5-10 minutes**: Best for security-critical operations (login, password reset)
- **30-60 minutes**: Acceptable for registration flows
- **Longer**: Only if you have a specific use case

.. warning::
   Longer expiration times increase the window for brute-force attacks. Consider implementing rate limiting.

VERIFY_SECURITY_CODE_ONLY_ONCE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Type:** ``bool``

**Required:** Yes

Whether a security code can be verified multiple times or only once.

.. code-block:: python

    "VERIFY_SECURITY_CODE_ONLY_ONCE": True   # Code can only be used once (recommended)
    "VERIFY_SECURITY_CODE_ONLY_ONCE": False  # Code can be reused within expiration window

**When to use ``True`` (recommended):**

- User registration
- Login / 2FA
- Password reset
- Any security-sensitive operation

**When to use ``False``:**

- Testing/development
- Marketing campaigns where users might need to re-verify
- Specific workflows requiring multiple verifications with the same code

.. note::
   When ``True``, attempting to verify an already-verified code returns the ``SECURITY_CODE_VERIFIED`` error.

Backend-Specific Settings
--------------------------

These settings are specific to certain backends but follow the same configuration pattern.

Sandbox Mode
^^^^^^^^^^^^

Sandbox backends are useful for development and testing without sending real SMS or consuming credits.

**TwilioSandboxBackend:**

.. code-block:: python

    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.twilio.TwilioSandboxBackend",
        "OPTIONS": {
            "SID": "fake_sid",
            "SECRET": "fake_secret",
            "FROM": "+15551234567",
            "SANDBOX_TOKEN": "123456",  # All codes will be "123456"
        },
        ...
    }

**NexmoSandboxBackend:**

.. code-block:: python

    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.nexmo.NexmoSandboxBackend",
        "OPTIONS": {
            "KEY": "fake_key",
            "SECRET": "fake_secret",
            "FROM": "TestApp",
            "SANDBOX_TOKEN": "999999",  # All codes will be "999999"
        },
        ...
    }

**Behavior:**

- ``generate_security_code()`` returns the fixed ``SANDBOX_TOKEN``
- ``validate_security_code()`` always returns valid (if code matches ``SANDBOX_TOKEN``)
- No actual SMS is sent (but ``send_sms`` may still be called)

Environment-Based Configuration
-------------------------------

It's common to use different settings for development, staging, and production:

.. code-block:: python

    # settings.py
    import os

    DEBUG = os.getenv("DEBUG", "False") == "True"

    if DEBUG:
        # Development: Use sandbox
        PHONE_VERIFICATION = {
            "BACKEND": "phone_verify.backends.twilio.TwilioSandboxBackend",
            "OPTIONS": {
                "SID": "fake",
                "SECRET": "fake",
                "FROM": "+15551234567",
                "SANDBOX_TOKEN": "123456",
            },
            "TOKEN_LENGTH": 6,
            "MESSAGE": "[DEV] Your code is {security_code}",
            "APP_NAME": "MyApp Dev",
            "SECURITY_CODE_EXPIRATION_TIME": 7200,  # Longer for testing
            "VERIFY_SECURITY_CODE_ONLY_ONCE": False,  # Allow retries
        }
    else:
        # Production: Use real SMS
        PHONE_VERIFICATION = {
            "BACKEND": "phone_verify.backends.twilio.TwilioBackend",
            "OPTIONS": {
                "SID": os.getenv("TWILIO_SID"),
                "SECRET": os.getenv("TWILIO_SECRET"),
                "FROM": os.getenv("TWILIO_FROM_NUMBER"),
            },
            "TOKEN_LENGTH": 6,
            "MESSAGE": "Your {app} verification code is {security_code}",
            "APP_NAME": "MyApp",
            "SECURITY_CODE_EXPIRATION_TIME": 600,  # 10 minutes
            "VERIFY_SECURITY_CODE_ONLY_ONCE": True,
        }

Using Environment Variables
----------------------------

Store sensitive credentials in environment variables, not in your code:

.. code-block:: python

    # settings.py
    import os

    PHONE_VERIFICATION = {
        "BACKEND": os.getenv(
            "PHONE_VERIFY_BACKEND",
            "phone_verify.backends.twilio.TwilioBackend"
        ),
        "OPTIONS": {
            "SID": os.getenv("TWILIO_SID"),
            "SECRET": os.getenv("TWILIO_SECRET"),
            "FROM": os.getenv("TWILIO_FROM_NUMBER"),
        },
        "TOKEN_LENGTH": int(os.getenv("PHONE_VERIFY_TOKEN_LENGTH", "6")),
        "MESSAGE": os.getenv(
            "PHONE_VERIFY_MESSAGE",
            "Your {app} code is {security_code}"
        ),
        "APP_NAME": os.getenv("PHONE_VERIFY_APP_NAME", "MyApp"),
        "SECURITY_CODE_EXPIRATION_TIME": int(
            os.getenv("PHONE_VERIFY_EXPIRATION", "600")
        ),
        "VERIFY_SECURITY_CODE_ONLY_ONCE": os.getenv(
            "PHONE_VERIFY_ONCE", "True"
        ) == "True",
    }

.. code-block:: shell

    # .env file
    TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_SECRET=your_auth_token
    TWILIO_FROM_NUMBER=+15551234567
    PHONE_VERIFY_TOKEN_LENGTH=6
    PHONE_VERIFY_EXPIRATION=600
    PHONE_VERIFY_ONCE=True

Multi-Backend Configuration
----------------------------

If you need to support multiple SMS providers (e.g., Twilio as primary, Nexmo as fallback), you can implement this in your custom backend:

.. code-block:: python

    # myapp/backends.py
    from phone_verify.backends.base import BaseBackend
    from phone_verify.backends.twilio import TwilioBackend
    from phone_verify.backends.nexmo import NexmoBackend

    class FallbackBackend(BaseBackend):
        def __init__(self, **options):
            super().__init__(**options)
            self.primary = TwilioBackend(**options.get("primary", {}))
            self.fallback = NexmoBackend(**options.get("fallback", {}))

        def send_sms(self, number, message):
            try:
                self.primary.send_sms(number, message)
            except Exception as e:
                logger.warning(f"Primary backend failed: {e}, using fallback")
                self.fallback.send_sms(number, message)

        def send_bulk_sms(self, numbers, message):
            # Similar logic
            pass

.. code-block:: python

    # settings.py
    PHONE_VERIFICATION = {
        "BACKEND": "myapp.backends.FallbackBackend",
        "OPTIONS": {
            "primary": {
                "SID": "...",
                "SECRET": "...",
                "FROM": "+15551234567",
            },
            "fallback": {
                "KEY": "...",
                "SECRET": "...",
                "FROM": "MyApp",
            },
        },
        ...
    }

Validation and Defaults
------------------------

The library validates that all required settings are present on initialization. Missing settings will raise ``ImproperlyConfigured``.

There are no built-in defaults for most settings because the correct values depend on your use case. You must explicitly configure all required settings.

Best Practices
--------------

1. **Use environment variables** for all credentials
2. **Different configs for different environments** (dev/staging/prod)
3. **Short expiration times** for security-sensitive operations
4. **Enable VERIFY_SECURITY_CODE_ONLY_ONCE** in production
5. **Use sandbox backends** in tests to avoid sending real SMS
6. **Log configuration errors** clearly in your application
7. **Document your settings** in your project's README

Example: Complete Production Configuration
-------------------------------------------

.. code-block:: python

    # settings.py
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Phone Verification Configuration
    PHONE_VERIFICATION = {
        # Backend
        "BACKEND": "phone_verify.backends.twilio.TwilioBackend",

        # Provider Credentials (from environment)
        "OPTIONS": {
            "SID": os.getenv("TWILIO_ACCOUNT_SID"),
            "SECRET": os.getenv("TWILIO_AUTH_TOKEN"),
            "FROM": os.getenv("TWILIO_PHONE_NUMBER"),
        },

        # Security Code Settings
        "TOKEN_LENGTH": 6,
        "SECURITY_CODE_EXPIRATION_TIME": 600,  # 10 minutes
        "VERIFY_SECURITY_CODE_ONLY_ONCE": True,

        # Message Settings
        "APP_NAME": "Acme Corporation",
        "MESSAGE": "Your Acme verification code is {security_code}. Valid for 10 minutes.",
    }

    # Installed Apps
    INSTALLED_APPS = [
        ...
        'phone_verify',
        'rest_framework',
        'phonenumber_field',
        ...
    ]

See Also
--------

- :doc:`getting_started` - Basic setup guide
- :doc:`customization` - Creating custom backends
- :doc:`troubleshooting` - Configuration troubleshooting
