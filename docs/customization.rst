.. _customization:

Customization Guide
===================

``django-phone-verify`` allows you to plug in your own SMS backend by extending the base backend interface.
This lets you use any third-party service such as AWS SNS, MessageBird, Plivo, etc.

This guide walks you through creating:

1. A custom SMS backend (example: Nexmo)
2. A sandbox version for testing


Creating a Custom SMS Backend
-----------------------------

This example demonstrates how to integrate Nexmo. The same pattern applies to any other provider.

Step 1: Create the Backend File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a new Python file in your Django project, e.g., ``nexmo.py``.

Step 2: Configure Django Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
        'SECURITY_CODE_EXPIRATION_SECONDS': 3600,
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,
    }

.. note::
   You can use an official client library like ``nexmo``, or make raw API calls.

Step 3: Implement the Backend Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import nexmo
    from nexmo.errors import ClientError
    from phone_verify.backends.base import BaseBackend

    class NexmoBackend(BaseBackend):
        def __init__(self, **options):
            super().__init__(**options)
            options = {key.lower(): value for key, value in options.items()}
            self._key = options.get("key")
            self._secret = options.get("secret")
            self._from = options.get("from")
            self.client = nexmo.Client(key=self._key, secret=self._secret)
            # Errors of this type raised while sending are logged and swallowed.
            self.exception_class = ClientError

        def send_sms(self, number, message):
            self.client.send_message({
                'from': self._from,
                'to': number,
                'text': message,
            })

        def generate_message(self, security_code, context=None):
            """You can optionally override the message formatting by
            defining a `generate_message()` method in your backend.
            This method receives the `security_code` and an optional
            `context` dictionary passed at runtime, giving you more
            flexibility than using a static `MESSAGE` template."""
            username = context.get("username", "User") if context else "User"
            return f"Hi {username}, your OTP is {security_code}."

``send_sms`` is the only abstract method on ``BaseBackend``; it is the one method every
backend must implement.

What ``exception_class`` Is For
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``send_security_code_and_generate_session_token()`` wraps the send call in
``except backend.exception_class``, logging the failure rather than letting it bubble up to
the caller. Set ``exception_class`` to your provider client's exception type so that only
provider errors are swallowed. ``BaseBackend`` defaults it to ``Exception``, which catches
everything, including bugs in your own code, so it is worth narrowing.

Do You Need ``send_bulk_sms``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No. ``BaseBackend.send_bulk_sms()`` is concrete: it loops over the numbers and calls your
``send_sms()`` for each one. Override it only if your provider exposes a native bulk send
endpoint, so that one API call replaces N. An override whose body is just that same loop is
redundant and should be deleted.


Creating a Sandbox SMS Backend
------------------------------

A sandbox backend is useful for testing flows without sending real SMS messages.

Step 1: Implement the Sandbox Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Subclass your production backend and override only two hooks. This is the pattern the
shipped ``TwilioSandboxBackend`` and ``NexmoSandboxBackend`` use.

.. code-block:: python

    class NexmoSandboxBackend(NexmoBackend):
        def __init__(self, **options):
            super().__init__(**options)
            options = {key.lower(): value for key, value in options.items()}
            self._token = options.get("sandbox_token")

        def generate_security_code(self):
            """Always issue the fixed sandbox token instead of a random code."""
            return self._token

        def _should_bypass_code_check(self, security_code):
            """Accept the sandbox token without a database code comparison."""
            return security_code == self._token

Because it subclasses ``NexmoBackend``, the sandbox inherits ``send_sms``,
``generate_message`` and ``exception_class`` unchanged. Nothing else needs restating.

.. warning::
   Do not override ``validate_security_code()`` wholesale to return
   ``SECURITY_CODE_VALID`` unconditionally. That method is where expiry, one-time use and
   the ``MAX_FAILED_ATTEMPTS`` brute-force lockout are enforced, so replacing it silently
   disables all three. It also accepts *any* code from *any* session token, not just the
   sandbox token, so the sandbox stops exercising the real flow.

   ``_should_bypass_code_check()`` exists precisely to avoid this: it skips only the code
   comparison, and ``validate_security_code()`` still applies the failed-attempts limit
   before honouring the bypass.

Step 2: Configure Django to Use the Sandbox Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
        'SECURITY_CODE_EXPIRATION_SECONDS': 3600,
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,
    }

----

You’re now ready to use your own backend with ``django-phone-verify``.
In production, configure the ``BACKEND`` setting to point to your real backend class.

