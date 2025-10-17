.. _troubleshooting:

Troubleshooting
===============

This guide covers common issues and their solutions when using ``django-phone-verify``.

Installation Issues
-------------------

ImportError: No module named 'twilio' or 'nexmo'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** You get an import error when the backend tries to load.

**Solution:** Install the required backend package:

.. code-block:: shell

    # For Twilio
    pip install django-phone-verify[twilio]

    # For Nexmo
    pip install django-phone-verify[nexmo]

    # For both
    pip install django-phone-verify[all]

The core package doesn't include SMS provider libraries by default to keep it lightweight.

Configuration Errors
--------------------

ImproperlyConfigured: Please define PHONE_VERIFICATION in settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** Django can't find the ``PHONE_VERIFICATION`` configuration.

**Solution:** Add the configuration dictionary to your ``settings.py``:

.. code-block:: python

    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.twilio.TwilioBackend",
        "OPTIONS": {
            "SID": "your-sid",
            "SECRET": "your-secret",
            "FROM": "+15551234567",
        },
        "TOKEN_LENGTH": 6,
        "MESSAGE": "Your code is {security_code}",
        "APP_NAME": "MyApp",
        "SECURITY_CODE_EXPIRATION_TIME": 3600,
        "VERIFY_SECURITY_CODE_ONLY_ONCE": False,
    }

ImproperlyConfigured: Please specify following settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** Some required settings keys are missing.

**Solution:** Ensure all required keys are present:

- ``BACKEND``
- ``OPTIONS``
- ``TOKEN_LENGTH``
- ``MESSAGE``
- ``APP_NAME``
- ``SECURITY_CODE_EXPIRATION_TIME``
- ``VERIFY_SECURITY_CODE_ONLY_ONCE``

Even if you don't need to customize them, you must include all keys with at least their default values.

SMS Sending Issues
------------------

SMS Not Being Received
^^^^^^^^^^^^^^^^^^^^^^^

**Possible Causes and Solutions:**

1. **Wrong phone number format**

   Ensure phone numbers are in E.164 format (``+<country_code><number>``):

   .. code-block:: python

      # ✅ Correct
      "+14155551234"

      # ❌ Incorrect
      "4155551234"
      "(415) 555-1234"

2. **Twilio/Nexmo credentials are incorrect**

   Verify your credentials in the provider's dashboard. Test with a simple script:

   .. code-block:: python

      from twilio.rest import Client

      client = Client("your_sid", "your_secret")
      message = client.messages.create(
          body="Test",
          from_="+15551234567",
          to="+15559876543"
      )
      print(message.sid)

3. **Phone number not verified (Sandbox mode)**

   If you're using a trial account, you may need to verify recipient numbers in your provider dashboard first.

4. **Rate limiting**

   Check if your SMS provider is rate-limiting your requests. Implement exponential backoff or contact your provider.

5. **Network/Firewall issues**

   Ensure your server can make outbound HTTPS requests to your SMS provider's API.

TwilioRestException or Nexmo Client Errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** SMS sending raises an exception from the provider.

**Solution:**

1. Check the exception message for specific error codes
2. Verify account balance/credits
3. Check that your ``FROM`` number is SMS-capable
4. Review provider-specific error documentation:
   - `Twilio Error Codes <https://www.twilio.com/docs/api/errors>`_
   - `Vonage Error Codes <https://developer.vonage.com/api-errors>`_

Verification Issues
-------------------

"Security code is not valid"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Possible Causes:**

1. **Typo in the code** - User entered wrong code
2. **Code expired** - Check ``SECURITY_CODE_EXPIRATION_TIME`` setting
3. **Database was cleared** - Security codes were deleted
4. **Different phone number** - Verification and code request used different numbers

**Solution:**

- Implement a "resend code" feature
- Increase expiration time if appropriate
- Log verification attempts to debug

"Session Token mis-match"
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** The session token provided doesn't match the one in the database.

**Causes:**

1. **Session token not stored correctly** on the client side
2. **Multiple registration attempts** - Old token being used with new code
3. **Token corruption** during transmission

**Solution:**

- Ensure client stores the full session token from ``/api/phone/register``
- Use the same token for verification that was returned during registration
- Check for any string truncation or encoding issues

"Security code has expired"
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** User took too long to enter the code.

**Solution:**

1. **Increase expiration time:**

   .. code-block:: python

      PHONE_VERIFICATION = {
          ...
          "SECURITY_CODE_EXPIRATION_TIME": 7200,  # 2 hours instead of 1
      }

2. **Implement resend functionality** - Let users request a new code

3. **Show countdown timer** in your UI to indicate remaining time

"Security code is already verified"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** Code was already used and ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is ``True``.

**Causes:**

1. **Double submission** - User clicked verify button twice
2. **Code reuse attempt** - User trying to verify multiple times

**Solution:**

- This is expected behavior for one-time codes
- If you need reusable codes, set ``VERIFY_SECURITY_CODE_ONLY_ONCE`` to ``False``
- Implement proper form/button disabling to prevent double submission

Database Issues
---------------

Unique Constraint Violation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** Error about unique constraint on ``(security_code, phone_number, session_token)``.

**Cause:** Extremely rare collision in randomly generated codes.

**Solution:** The library handles this by deleting old codes before creating new ones. If you're manually creating ``SMSVerification`` objects, ensure you follow the same pattern:

.. code-block:: python

    from phone_verify.models import SMSVerification

    # Delete old codes first
    SMSVerification.objects.filter(phone_number=phone_number).delete()

    # Then create new
    SMSVerification.objects.create(...)

Custom Backend Issues
---------------------

Backend Not Found
^^^^^^^^^^^^^^^^^

**Problem:** ``ModuleNotFoundError`` when loading your custom backend.

**Solution:**

1. Ensure the module path in ``BACKEND`` setting is correct
2. Check that your backend class inherits from ``BaseBackend``
3. Verify the Python module is in your ``PYTHONPATH``

Example for a backend in ``myapp/backends/sms.py``:

.. code-block:: python

    PHONE_VERIFICATION = {
        "BACKEND": "myapp.backends.sms.CustomBackend",
        ...
    }

"send_sms() missing required argument"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** Your custom backend's ``send_sms`` method signature is incorrect.

**Solution:** Ensure your backend implements the required methods with correct signatures:

.. code-block:: python

    from phone_verify.backends.base import BaseBackend

    class CustomBackend(BaseBackend):
        def send_sms(self, number, message):
            # number is a single phone number string
            # message is the SMS content
            pass

        def send_bulk_sms(self, numbers, message):
            # numbers is a list of phone number strings
            # message is the SMS content
            pass

Integration Issues
------------------

DRF ViewSet Not Found
^^^^^^^^^^^^^^^^^^^^^

**Problem:** 404 errors when accessing ``/api/phone/register`` or ``/api/phone/verify``.

**Solution:** Ensure you've registered the ViewSet in your URLs:

.. code-block:: python

    # urls.py
    from rest_framework.routers import DefaultRouter
    from phone_verify.api import VerificationViewSet

    router = DefaultRouter(trailing_slash=False)
    router.register('phone', VerificationViewSet, basename='phone')

    urlpatterns = [
        path('api/', include(router.urls)),
    ]

Serializer Validation Fails Silently
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** Validation errors not being shown to the user.

**Solution:** Use ``raise_exception=True`` in your views:

.. code-block:: python

    serializer = SMSVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # This will return 400 with error details

Testing Issues
--------------

Tests Sending Real SMS
^^^^^^^^^^^^^^^^^^^^^^

**Problem:** Your test suite is sending actual SMS messages and consuming credits.

**Solution:** Use a sandbox backend or mock the SMS sending:

**Option 1: Sandbox Backend**

.. code-block:: python

    # test_settings.py
    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.twilio.TwilioSandboxBackend",
        "OPTIONS": {
            "SANDBOX_TOKEN": "123456",  # Fixed code for tests
            ...
        },
        ...
    }

**Option 2: Mock with pytest**

.. code-block:: python

    from unittest.mock import patch

    @patch('phone_verify.backends.twilio.TwilioBackend.send_sms')
    def test_verification(mock_send_sms):
        # Your test code here
        mock_send_sms.assert_called_once()

**Option 3: Custom Test Backend**

.. code-block:: python

    from phone_verify.backends.base import BaseBackend

    class TestBackend(BaseBackend):
        def send_sms(self, number, message):
            pass  # No-op

        def send_bulk_sms(self, numbers, message):
            pass

Performance Issues
------------------

Slow API Responses
^^^^^^^^^^^^^^^^^^

**Problem:** ``/api/phone/register`` takes too long to respond.

**Causes and Solutions:**

1. **SMS provider latency** - Consider sending SMS asynchronously:

   .. code-block:: python

      from celery import shared_task
      from phone_verify.services import PhoneVerificationService

      @shared_task
      def send_verification_async(phone_number, security_code):
          service = PhoneVerificationService(phone_number)
          service.send_verification(phone_number, security_code)

2. **Database queries** - Ensure your database has appropriate indexes (they're included in migrations)

3. **Network issues** - Check connectivity to your SMS provider

Too Many Database Records
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** ``sms_verification`` table growing too large.

**Solution:** Implement a cleanup task to delete old verifications:

.. code-block:: python

    from django.utils import timezone
    from datetime import timedelta
    from phone_verify.models import SMSVerification

    # Delete verifications older than 7 days
    cutoff = timezone.now() - timedelta(days=7)
    SMSVerification.objects.filter(created_at__lt=cutoff).delete()

Run this periodically with a cron job or Celery beat task.

Getting Help
------------

If your issue isn't covered here:

1. **Check GitHub Issues**: `<https://github.com/CuriousLearner/django-phone-verify/issues>`_
2. **Review Recent Changes**: :doc:`changelog`
3. **Enable Debug Logging**:

   .. code-block:: python

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

4. **Open a new issue** with:
   - Django version
   - Python version
   - ``django-phone-verify`` version
   - Backend being used
   - Full traceback
   - Minimal reproducible example
