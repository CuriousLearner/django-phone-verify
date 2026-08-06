.. _faq:

Frequently Asked Questions (FAQ)
=================================

This page answers common questions about ``django-phone-verify``.

General Questions
-----------------

**Q: What is django-phone-verify used for?**

``django-phone-verify`` is a Django library for verifying phone numbers via SMS. Common use cases include:

- User registration/signup phone verification
- Two-factor authentication (2FA)
- Account recovery / password reset
- Phone number update verification
- Marketing opt-in confirmation

**Q: Which SMS providers are supported?**

Out of the box, ``django-phone-verify`` supports:

- **Twilio** - via ``phone_verify.backends.twilio.TwilioBackend``
- **Nexmo/Vonage** - via ``phone_verify.backends.nexmo.NexmoBackend``

You can also write custom backends for any SMS provider (AWS SNS, MessageBird, Plivo, etc.). See :doc:`customization`.

**Q: Do I need Django REST Framework?**

Not necessarily. DRF is only required if you want to use the built-in API viewsets (``POST /api/phone/register`` and ``POST /api/phone/verify``).

You can use the core services directly in standard Django views without DRF. See :doc:`integration` for non-DRF examples.

**Q: Does this work with custom user models?**

Yes! ``django-phone-verify`` doesn't touch your user model at all. It stores verification data in its own ``SMSVerification`` model, so it works with any ``AUTH_USER_MODEL``.

Installation & Configuration
-----------------------------

**Q: Which installation command should I use?**

- For most users: ``pip install django-phone-verify[twilio]`` or ``pip install django-phone-verify[nexmo]``
- If you want both backends: ``pip install django-phone-verify[all]``
- If writing a custom backend: ``pip install django-phone-verify``

**Q: What's the minimum Django/Python version?**

- Python 3.8+ (Python 3.7 and below are EOL)
- Django 2.1+
- Django REST Framework 3.9+ (if using the API viewsets)

**Q: Where should I store my Twilio/Nexmo credentials?**

**Never hardcode credentials in your settings.py!** Use environment variables:

.. code-block:: python

    # settings.py
    import os

    PHONE_VERIFICATION = {
        'OPTIONS': {
            'SID': os.environ.get('TWILIO_ACCOUNT_SID'),
            'SECRET': os.environ.get('TWILIO_AUTH_TOKEN'),
            'FROM': os.environ.get('TWILIO_PHONE_NUMBER'),
        },
        # ... other settings
    }

Store actual credentials in a ``.env`` file (added to ``.gitignore``) or use a secrets manager. See :doc:`security` for more details.

Security & Best Practices
--------------------------

**Q: How do I prevent brute-force attacks on security codes?**

Two layers, and you want both.

**1. Per-record lockout (built in, on by default).** Every ``SMSVerification`` row carries a
``failed_attempts`` counter. Each wrong, expired or already-used code increments it; once it
reaches ``MAX_FAILED_ATTEMPTS`` (default ``5``) that record is locked and every further
attempt returns ``SECURITY_CODE_TOO_MANY_ATTEMPTS`` until the user requests a new code. A
successful verification resets the counter to zero.

.. code-block:: python

    PHONE_VERIFICATION = {
        'MAX_FAILED_ATTEMPTS': 5,
        # ... other settings
    }

**2. Request rate limiting (your job).** The lockout is scoped to one verification record, so
it does not stop an attacker from repeatedly hitting ``register`` to burn your SMS budget, nor
from spraying codes across many phone numbers. Rate limit the endpoints themselves. See the
:doc:`security` guide for strategies using:

- Django Ratelimit
- DRF Throttling
- Cache-based rate limiting

**Q: What's a good SECURITY_CODE_EXPIRATION_SECONDS value?**

We recommend **300-600 seconds (5-10 minutes)**. This balances security and user experience:

- Too short (< 5 min): Users may not receive/enter the code in time
- Too long (> 10 min): Increases window for brute-force attacks

**Q: Should I set VERIFY_SECURITY_CODE_ONLY_ONCE to True?**

**Yes, for high-security applications.** This ensures codes can only be used once, even if they haven't expired.

For low-risk use cases (e.g., marketing opt-in), you can set it to ``False`` to allow retry attempts.

**Q: How do I handle GDPR/privacy compliance?**

Phone numbers are personally identifiable information (PII). Best practices:

1. Don't log phone numbers in plain text
2. Delete old ``SMSVerification`` records periodically
3. Provide a way for users to delete their data
4. Include phone verification in your privacy policy
5. Only send SMS to users who have consented

See the :doc:`security` guide for detailed compliance guidance.

Usage & Integration
-------------------

**Q: Can I customize the SMS message?**

Yes, in two ways:

**1. Static message template (in settings):**

.. code-block:: python

    PHONE_VERIFICATION = {
        'MESSAGE': 'Hi! Your {app} verification code is {security_code}.',
        'APP_NAME': 'MyApp',
        # ...
    }

**2. Dynamic messages (in custom backend):**

Override ``generate_message()`` in your backend to create context-aware messages:

.. code-block:: python

    class CustomBackend(TwilioBackend):
        def generate_message(self, security_code, context=None):
            username = context.get('username', 'User') if context else 'User'
            return f"Hi {username}, your code is {security_code}."

See :doc:`advanced_examples` for more details.

**Q: How do I test without sending real SMS?**

Use the shipped ``phone_verify.backends.twilio.TwilioSandboxBackend`` (or
``NexmoSandboxBackend``) and set ``SANDBOX_TOKEN`` in ``OPTIONS``. To roll your own, subclass
your production backend and override the two sandbox hooks:

.. code-block:: python

    class TwilioSandboxBackend(TwilioBackend):
        def __init__(self, **options):
            super().__init__(**options)
            options = {key.lower(): value for key, value in options.items()}
            self._token = options.get('sandbox_token')

        def generate_security_code(self):
            return self._token

        def _should_bypass_code_check(self, security_code):
            return security_code == self._token

Then use this backend in development/testing environments. Do not override
``validate_security_code()`` instead: it enforces expiry, one-time use and the brute-force
lockout. See :doc:`customization`.

**Q: Can I use this for 2FA (two-factor authentication)?**

Yes! See :doc:`advanced_examples` for a complete 2FA implementation example including:

- Login flow with SMS verification
- Backend + frontend integration
- Session management

**Q: How do I implement phone number updates?**

See the "Phone Number Update Flow" example in :doc:`advanced_examples`, which includes:

- Verify new phone number before updating
- Only update if verification succeeds
- Prevent account takeover attempts

Troubleshooting
---------------

**Q: I'm getting "ImproperlyConfigured" errors**

This usually means ``PHONE_VERIFICATION`` is missing or misconfigured in your ``settings.py``. Make sure:

1. ``PHONE_VERIFICATION`` dict exists in ``settings.py``
2. All required keys are present (``BACKEND``, ``OPTIONS``, etc.)
3. Environment variables are loaded correctly

See :doc:`troubleshooting` for detailed solutions.

**Q: SMS messages aren't being sent**

Check the following:

1. **Credentials**: Are your Twilio/Nexmo credentials correct?
2. **Phone number format**: Use E.164 format (e.g., ``+1234567890``)
3. **Provider account**: Is your Twilio/Nexmo account active and funded?
4. **Provider restrictions**: Some providers require phone number verification before sending SMS
5. **Logs**: Check Django logs for error messages

See the "SMS Sending Problems" section in :doc:`troubleshooting`.

**Q: Verification always fails even with correct code**

Common causes:

1. **Locked out**: After ``MAX_FAILED_ATTEMPTS`` (default ``5``) failures the record is locked
   and returns ``SECURITY_CODE_TOO_MANY_ATTEMPTS`` even for the correct code. The counter only
   clears on a successful verification, so the user must request a new code
2. **Code expired**: Check ``SECURITY_CODE_EXPIRATION_SECONDS`` setting
3. **Session token mismatch**: Ensure you're using the same ``session_token`` from registration
4. **Already verified**: If ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is True, codes can only be used once
5. **Clock skew**: Expiry compares the record's ``created_at`` against ``timezone.now()``, so a
   server clock that jumps can expire codes early

See :doc:`troubleshooting` for debugging steps.

**Q: How do I debug verification issues?**

Enable Django logging to see detailed error messages:

.. code-block:: python

    # settings.py
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'phone_verify': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }

Performance & Scaling
---------------------

**Q: Can I send SMS asynchronously to improve API response time?**

Yes! Use Celery or another task queue. Example:

.. code-block:: python

    # tasks.py
    from celery import shared_task
    from phone_verify.services import send_security_code_and_generate_session_token

    @shared_task
    def send_verification_code_async(phone_number):
        # Creates the record, sends the SMS, and returns the session token.
        return send_security_code_and_generate_session_token(phone_number)

Note that the session token is only available once the task runs, so the caller has to collect
it from the task result rather than from the request that queued it.

See :doc:`advanced_examples` for a complete async implementation.

**Q: How do I handle high volumes of verification requests?**

1. **Use async SMS sending** (see above)
2. **Implement rate limiting** to prevent abuse
3. **Use database connection pooling** for better performance
4. **Consider a dedicated SMS queue** for reliability
5. **Monitor costs** - SMS can get expensive at scale

**Q: Should I delete old SMSVerification records?**

Yes, for both performance and privacy reasons. There is no need to write your own; the package
ships a management command:

.. code-block:: shell

    # Delete records older than RECORD_RETENTION_DAYS (default 30)
    python manage.py cleanup_phone_verifications

    # Preview what would be deleted, without deleting
    python manage.py cleanup_phone_verifications --dry-run

    # Override the retention window for a single run
    python manage.py cleanup_phone_verifications --days 7

Set the default window in settings and run the command from cron or a periodic task:

.. code-block:: python

    PHONE_VERIFICATION = {
        'RECORD_RETENTION_DAYS': 30,
        # ... other settings
    }

Advanced Usage
--------------

**Q: Can I use multiple SMS backends in the same project?**

Not directly, but you can create a wrapper backend that routes to different providers. See :doc:`advanced_examples` for a "Fallback SMS Provider" example.

**Q: How do I send bulk verification SMS?**

Use the ``send_bulk_sms()`` method in your backend:

.. code-block:: python

    from phone_verify.backends.twilio import TwilioBackend

    backend = TwilioBackend(**settings.PHONE_VERIFICATION['OPTIONS'])
    phone_numbers = ['+1234567890', '+0987654321']
    message = "Your verification code is 123456"
    backend.send_bulk_sms(phone_numbers, message)

**Q: Can I integrate this with third-party authentication (OAuth, social login)?**

Yes! After social login, you can still verify the phone number:

.. code-block:: python

    from phone_verify.services import send_security_code_and_generate_session_token

    # After successful OAuth login
    user = request.user
    phone_number = request.data.get('phone_number')

    # Send verification
    session_token = send_security_code_and_generate_session_token(phone_number)

    # Later, after verification succeeds, link to user
    user.phone_number = phone_number
    user.phone_verified = True
    user.save()

Still Have Questions?
---------------------

- Check the :doc:`troubleshooting` guide for common issues
- Review the :doc:`api_reference` for detailed API documentation
- Open an issue on `GitHub <https://github.com/CuriousLearner/django-phone-verify/issues>`_
- Read the full documentation at `https://django-phone-verify.readthedocs.io/ <https://django-phone-verify.readthedocs.io/>`_
