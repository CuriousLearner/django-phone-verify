Customization
=============

You can use a custom SMS backend by extending the default interface provided by
``phone_verify.backends.base.BaseBackend``. This allows you to integrate any third-party SMS service
such as AWS SNS, MessageBird, Plivo, etc.

The following guide demonstrates how to write a custom backend using **Nexmo** as an example.
The steps are similar for any other SMS provider.

Step 1: Create the Backend File
-------------------------------

Create a new Python file in your project, e.g., ``nexmo.py``.

Step 2: Configure Settings
--------------------------

Add the following to your Django ``settings.py``:

.. code-block:: python

    # Settings for phone_verify
    PHONE_VERIFICATION = {
        'BACKEND': 'nexmo.NexmoBackend',  # Path to your custom backend class
        'OPTIONS': {
            'KEY': 'Fake Key',
            'SECRET': 'Fake Secret',
            'FROM': '+1234567890',
            'SANDBOX_TOKEN': '123456',  # Optional: used for sandbox/testing
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600,  # In seconds
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,
    }

.. note::
   You can use a client library for your service or directly invoke its API. In this example,
   we will use the official ``nexmo`` client library.

Step 3: Create the Backend Class
--------------------------------

Inside ``nexmo.py``, define the custom backend class:

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

Step 4: Implement `send_sms` and `send_bulk_sms`
------------------------------------------------

The methods ``send_sms`` and ``send_bulk_sms`` must be overridden:

- ``send_sms(number, message)`` sends a single message.
- ``send_bulk_sms(numbers, message)`` sends the message to multiple recipients.

How to Create a Custom Sandbox Backend
======================================

If you want to implement a sandbox (testing) version of your backend, follow similar steps.
In addition, override a few more methods.

Step 1: Define Sandbox Class
----------------------------

Create a new class ``NexmoSandboxBackend`` extending ``BaseBackend``:

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
            """
            Return a fixed token for sandbox/testing purposes.
            """
            return self._token

        def validate_security_code(self, security_code, phone_number, session_token):
            """
            Always treat the provided token as valid for testing.
            """
            return SMSVerification.objects.none(), self.SECURITY_CODE_VALID

.. note::
   - ``generate_security_code`` returns a constant code for testing purposes.
   - ``validate_security_code`` always returns a valid result for any given input.

Step 2: Update Settings
-----------------------

To use the sandbox backend, update your settings:

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

You now have a fully customizable and testable SMS backend using `django-phone-verify`.
For production, point the `BACKEND` to your real service class.
