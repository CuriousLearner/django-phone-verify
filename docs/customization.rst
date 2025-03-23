.. _customization:

Customization Guide
===================

``django-phone-verify`` allows you to plug in your own SMS backend by extending the base backend interface.
This lets you use any third-party service such as AWS SNS, MessageBird, Plivo, etc.

This guide walks you through creating:

1. A custom SMS backend (example: Nexmo)
2. A sandbox version for testing


Custom SMS Backend (Example: Nexmo)
-----------------------------------

### Step 1: Create a Backend File

Create a new Python file in your Django project (e.g., ``nexmo.py``).

### Step 2: Configure Settings

Update your ``settings.py``:

.. code-block:: python

    PHONE_VERIFICATION = {
        'BACKEND': 'nexmo.NexmoBackend',
        'OPTIONS': {
            'KEY': 'Fake Key',
            'SECRET': 'Fake Secret',
            'FROM': '+1234567890',
            'SANDBOX_TOKEN': '123456',
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600,
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,
    }

.. note::
   You can use a client library (like ``nexmo``) or directly call the API endpoints of the SMS provider.

### Step 3: Implement Backend Class

.. code-block:: python

    import nexmo
    from phone_verify.backends.base import BaseBackend

    class NexmoBackend(BaseBackend):
        def __init__(self, **options):
            super().__init__(**options)
            options = {key.lower(): value for key, value in options.items()}
            self._key = options.get("key")
            self._secret = options.get("secret")
            self._from = options.get("from")
            self.client = nexmo.Client(key=self._key, secret=self._secret)

        def send_sms(self, number, message):
            self.client.send_message({
                'from': self._from,
                'to': number,
                'text': message,
            })

        def send_bulk_sms(self, numbers, message):
            for number in numbers:
                self.send_sms(number, message)


Custom Sandbox Backend (Example: Nexmo)
---------------------------------------

A sandbox backend is useful for testing flows without sending real SMS messages.

### Step 1: Create Sandbox Backend

.. code-block:: python

    import nexmo
    from phone_verify.backends.base import BaseBackend
    from phone_verify.models import SMSVerification

    class NexmoSandboxBackend(BaseBackend):
        def __init__(self, **options):
            super().__init__(**options)
            options = {key.lower(): value for key, value in options.items()}
            self._key = options.get("key")
            self._secret = options.get("secret")
            self._from = options.get("from")
            self._token = options.get("sandbox_token")
            self.client = nexmo.Client(key=self._key, secret=self._secret)

        def send_sms(self, number, message):
            self.client.send_message({
                'from': self._from,
                'to': number,
                'text': message,
            })

        def send_bulk_sms(self, numbers, message):
            for number in numbers:
                self.send_sms(number, message)

        def generate_security_code(self):
            return self._token

        def validate_security_code(self, security_code, phone_number, session_token):
            return SMSVerification.objects.none(), self.SECURITY_CODE_VALID

.. note::
   - ``generate_security_code`` returns a constant token for predictable testing.
   - ``validate_security_code`` always returns a valid result.

### Step 2: Use Sandbox in Settings

.. code-block:: python

    PHONE_VERIFICATION = {
        'BACKEND': 'nexmo.NexmoSandboxBackend',
        'OPTIONS': {
            'KEY': 'Fake Key',
            'SECRET': 'Fake Secret',
            'FROM': '+1234567890',
            'SANDBOX_TOKEN': '123456',
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600,
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,
    }

----

You're now ready to use a fully custom or sandbox backend with ``django-phone-verify``.
For production, update the ``BACKEND`` to your live implementation.
