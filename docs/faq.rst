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

Not necessarily. DRF is only required if you want to use the built-in API viewsets (``/api/phone/register/`` and ``/api/phone/verify/``).

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

You should implement **rate limiting** on your verification endpoints. See the :doc:`security` guide for multiple rate limiting strategies using:

- Django Ratelimit
- DRF Throttling
- Cache-based rate limiting

**Q: What's a good SECURITY_CODE_EXPIRATION_TIME value?**

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

Create a **sandbox backend** that returns a fixed code. Example:

.. code-block:: python

    class TwilioSandboxBackend(TwilioBackend):
        def generate_security_code(self):
            return self.options.get('SANDBOX_TOKEN', '123456')

Then use this backend in development/testing environments. See :doc:`customization`.

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

1. **Code expired**: Check ``SECURITY_CODE_EXPIRATION_TIME`` setting
2. **Session token mismatch**: Ensure you're using the same ``session_token`` from registration
3. **Already verified**: If ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is True, codes can only be used once
4. **Clock skew**: Ensure server time is accurate (for JWT token validation)

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
    from phone_verify.services import PhoneVerificationService

    @shared_task
    def send_verification_code_async(phone_number):
        service = PhoneVerificationService(phone_number)
        return service.send_verification()

See :doc:`advanced_examples` for a complete async implementation.

**Q: How do I handle high volumes of verification requests?**

1. **Use async SMS sending** (see above)
2. **Implement rate limiting** to prevent abuse
3. **Use database connection pooling** for better performance
4. **Consider a dedicated SMS queue** for reliability
5. **Monitor costs** - SMS can get expensive at scale

**Q: Should I delete old SMSVerification records?**

Yes, for both performance and privacy reasons. Create a management command or periodic task:

.. code-block:: python

    from django.utils import timezone
    from datetime import timedelta
    from phone_verify.models import SMSVerification

    # Delete records older than 30 days
    cutoff = timezone.now() - timedelta(days=30)
    SMSVerification.objects.filter(created_at__lt=cutoff).delete()

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

    # After successful OAuth login
    user = request.user
    phone_number = request.data.get('phone_number')

    # Send verification
    service = PhoneVerificationService(phone_number)
    session_token = service.send_verification()

    # Later, after verification succeeds, link to user
    user.phone_number = phone_number
    user.phone_verified = True
    user.save()

Still Have Questions?
---------------------

- Check the :doc:`troubleshooting` guide for common issues
- Review the :doc:`api_reference` for detailed API documentation
- Open an issue on `GitHub <https://github.com/CuriousLearner/django-phone-verify/issues>`_
- Read the full documentation at `https://www.sanyamkhurana.com/django-phone-verify/ <https://www.sanyamkhurana.com/django-phone-verify/>`_
