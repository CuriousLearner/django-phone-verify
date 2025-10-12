.. _security:

Security Best Practices
========================

Phone number verification is often used for security-sensitive operations like authentication and account recovery. This guide covers security best practices when using ``django-phone-verify``.

Rate Limiting
-------------

Why Rate Limiting is Critical
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Without rate limiting, attackers can:

1. **Brute-force verification codes** by trying many combinations
2. **Abuse SMS sending** to rack up costs or spam users
3. **Enumerate phone numbers** to discover which are registered

Implementing Rate Limiting
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Option 1: Django Ratelimit**

Install the package:

.. code-block:: shell

    pip install django-ratelimit

Apply rate limiting to your endpoints:

.. code-block:: python

    from django_ratelimit.decorators import ratelimit
    from rest_framework.decorators import action
    from phone_verify.api import VerificationViewSet

    class CustomVerificationViewSet(VerificationViewSet):

        @ratelimit(key='ip', rate='3/h', method='POST')
        @action(detail=False, methods=['POST'])
        def register(self, request):
            # Limit to 3 code requests per hour per IP
            return super().register(request)

        @ratelimit(key='ip', rate='10/h', method='POST')
        @action(detail=False, methods=['POST'])
        def verify(self, request):
            # Limit to 10 verification attempts per hour per IP
            return super().verify(request)

**Option 2: Django REST Framework Throttling**

.. code-block:: python

    from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

    class PhoneRegisterThrottle(AnonRateThrottle):
        rate = '3/hour'

    class PhoneVerifyThrottle(AnonRateThrottle):
        rate = '10/hour'

    class CustomVerificationViewSet(VerificationViewSet):
        throttle_classes = [PhoneRegisterThrottle]

        def get_throttles(self):
            if self.action == 'verify':
                return [PhoneVerifyThrottle()]
            return super().get_throttles()

**Option 3: Phone Number-Based Rate Limiting**

.. code-block:: python

    from django.core.cache import cache
    from rest_framework.exceptions import Throttled

    class CustomVerificationViewSet(VerificationViewSet):

        @action(detail=False, methods=['POST'])
        def register(self, request):
            phone_number = request.data.get('phone_number')

            # Check rate limit
            key = f"phone_verify:{phone_number}:register"
            attempts = cache.get(key, 0)

            if attempts >= 3:
                raise Throttled(detail="Too many requests. Try again later.")

            # Increment counter
            cache.set(key, attempts + 1, timeout=3600)  # 1 hour

            return super().register(request)

**Recommended Limits:**

- **Code requests**: 3-5 per hour per phone number
- **Verification attempts**: 5-10 per hour per phone number
- **Failed verifications**: Lock after 5 consecutive failures

Security Code Settings
----------------------

Token Length
^^^^^^^^^^^^

Use an appropriate token length based on your threat model:

.. code-block:: python

    PHONE_VERIFICATION = {
        "TOKEN_LENGTH": 6,  # Recommended minimum (1 million combinations)
        ...
    }

**Security Analysis:**

- **4 digits**: 10,000 combinations → Too weak, brute-forceable
- **6 digits**: 1,000,000 combinations → Standard, secure with rate limiting
- **8 digits**: 100,000,000 combinations → Very secure but harder for users

.. warning::
   Tokens of 4 digits or less are **not recommended** for production use.

Expiration Time
^^^^^^^^^^^^^^^

Use short expiration times for security-sensitive operations:

.. code-block:: python

    PHONE_VERIFICATION = {
        # Security-sensitive (login, 2FA, password reset)
        "SECURITY_CODE_EXPIRATION_TIME": 300,  # 5 minutes

        # Standard registration flows
        "SECURITY_CODE_EXPIRATION_TIME": 600,  # 10 minutes

        # Avoid longer times in production
        ...
    }

**Trade-offs:**

- **Shorter (5-10 min)**: Better security, may frustrate slow users
- **Longer (30-60 min)**: Better UX, higher security risk

One-Time Codes
^^^^^^^^^^^^^^

Always use one-time codes in production:

.. code-block:: python

    PHONE_VERIFICATION = {
        "VERIFY_SECURITY_CODE_ONLY_ONCE": True,  # Recommended for production
        ...
    }

This prevents:

- Code reuse by attackers
- Replay attacks
- Unauthorized verification attempts

Secure Storage
--------------

Credential Management
^^^^^^^^^^^^^^^^^^^^^

**Never hard-code credentials:**

.. code-block:: python

    # ❌ BAD - Credentials in source code
    PHONE_VERIFICATION = {
        "OPTIONS": {
            "SID": "AC1234567890abcdef",
            "SECRET": "my_secret_token",
        },
        ...
    }

**Use environment variables:**

.. code-block:: python

    # ✅ GOOD - Credentials from environment
    import os

    PHONE_VERIFICATION = {
        "OPTIONS": {
            "SID": os.getenv("TWILIO_ACCOUNT_SID"),
            "SECRET": os.getenv("TWILIO_AUTH_TOKEN"),
        },
        ...
    }

**Use a secrets manager (production):**

.. code-block:: python

    # ✅ BETTER - Use AWS Secrets Manager, HashiCorp Vault, etc.
    import boto3
    import json

    def get_secret(secret_name):
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])

    twilio_creds = get_secret("production/twilio")

    PHONE_VERIFICATION = {
        "OPTIONS": {
            "SID": twilio_creds["sid"],
            "SECRET": twilio_creds["secret"],
        },
        ...
    }

Database Security
^^^^^^^^^^^^^^^^^

1. **Encrypt sensitive data at rest** (use Django's database encryption or field-level encryption)
2. **Limit access** to the ``sms_verification`` table
3. **Regularly clean up** old verification records:

.. code-block:: python

    from django.utils import timezone
    from datetime import timedelta
    from phone_verify.models import SMSVerification

    # Delete records older than 30 days
    cutoff = timezone.now() - timedelta(days=30)
    SMSVerification.objects.filter(created_at__lt=cutoff).delete()

Session Token Security
^^^^^^^^^^^^^^^^^^^^^^^

Session tokens are JWTs signed with Django's ``SECRET_KEY``:

1. **Keep SECRET_KEY secret** and rotate it periodically
2. **Use a long, random SECRET_KEY** (at least 50 characters)
3. **Don't expose session tokens** in URLs or logs

.. code-block:: python

    # Generate a secure SECRET_KEY
    from django.core.management.utils import get_random_secret_key
    print(get_random_secret_key())

Phone Number Privacy
--------------------

Minimize PII Exposure
^^^^^^^^^^^^^^^^^^^^^

1. **Log carefully** - Don't log full phone numbers:

.. code-block:: python

    import logging

    logger = logging.getLogger(__name__)

    # ❌ BAD
    logger.info(f"Verification sent to {phone_number}")

    # ✅ GOOD - Mask phone number
    masked = phone_number[:3] + "****" + phone_number[-2:]
    logger.info(f"Verification sent to {masked}")

2. **Limit database retention** - Delete old verifications
3. **Encrypt phone numbers** if required by regulations (GDPR, CCPA)

User Consent
^^^^^^^^^^^^

Ensure you have user consent before sending SMS:

.. code-block:: python

    class PhoneVerificationForm(forms.Form):
        phone_number = forms.CharField()
        consent = forms.BooleanField(
            required=True,
            label="I consent to receive SMS messages for verification"
        )

Avoiding Information Disclosure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Don't reveal whether a phone number is registered:

.. code-block:: python

    # ❌ BAD - Reveals if phone is registered
    def register(self, request):
        phone = request.data['phone_number']
        if User.objects.filter(phone_number=phone).exists():
            return Response({"error": "Phone number already registered"}, status=400)
        # Send code
        ...

    # ✅ GOOD - Always send code (or pretend to)
    def register(self, request):
        phone = request.data['phone_number']
        # Always return success, but only send SMS if not registered
        if not User.objects.filter(phone_number=phone).exists():
            send_security_code_and_generate_session_token(phone)
        return Response({"message": "If this number is valid, you'll receive a code"})

Message Content Security
-------------------------

Avoid Phishing Risks
^^^^^^^^^^^^^^^^^^^^

Use clear, consistent branding in messages:

.. code-block:: python

    PHONE_VERIFICATION = {
        "MESSAGE": "Your Acme Corp verification code is {security_code}. "
                   "Never share this code with anyone, including Acme staff.",
        ...
    }

**Best Practices:**

- Include your app/company name
- Warn users not to share the code
- Don't include links (phishing risk)
- Keep messages concise

Prevent Message Injection
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you allow custom context in messages, sanitize inputs:

.. code-block:: python

    from django.utils.html import escape

    def send_custom_verification(phone_number, username):
        service = PhoneVerificationService(phone_number)

        # ❌ BAD - Allows injection
        context = {"username": username}

        # ✅ GOOD - Escape user input
        context = {"username": escape(username)[:20]}  # Limit length too

        service.send_verification(
            phone_number,
            "123456",
            context=context
        )

Testing and Sandbox Mode
-------------------------

Never Test in Production
^^^^^^^^^^^^^^^^^^^^^^^^^

Use sandbox backends for testing:

.. code-block:: python

    # Development settings
    PHONE_VERIFICATION = {
        "BACKEND": "phone_verify.backends.twilio.TwilioSandboxBackend",
        "OPTIONS": {
            "SANDBOX_TOKEN": "123456",
            ...
        },
        ...
    }

Separate Test Phone Numbers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you must test with real SMS:

1. Use dedicated test phone numbers
2. Never use real user numbers
3. Document all test numbers
4. Monitor costs closely

Monitoring and Alerting
------------------------

Monitor for Abuse
^^^^^^^^^^^^^^^^^

Set up alerts for:

1. **High SMS volume** - Unusual number of verification requests
2. **Failed verifications** - Many failed attempts (potential attack)
3. **Expensive operations** - SMS to international numbers
4. **API errors** - Twilio/Nexmo failures

.. code-block:: python

    # Example: Log suspicious activity
    import logging

    logger = logging.getLogger(__name__)

    class CustomVerificationViewSet(VerificationViewSet):

        @action(detail=False, methods=['POST'])
        def verify(self, request):
            phone = request.data.get('phone_number')
            code = request.data.get('security_code')

            # Check for repeated failures
            key = f"failed_verifications:{phone}"
            failures = cache.get(key, 0)

            try:
                response = super().verify(request)
                cache.delete(key)  # Reset on success
                return response
            except ValidationError:
                failures += 1
                cache.set(key, failures, timeout=3600)

                if failures >= 5:
                    logger.warning(
                        f"Suspicious activity: {failures} failed verifications for {phone[:3]}****"
                    )

                raise

Audit Logging
^^^^^^^^^^^^^

Log security-relevant events:

.. code-block:: python

    import logging

    logger = logging.getLogger('phone_verify.audit')

    def audit_log(event, phone_number, metadata=None):
        masked_phone = phone_number[:3] + "****" + phone_number[-2:]
        logger.info(f"{event} | phone={masked_phone} | metadata={metadata}")

    # Usage
    audit_log("code_sent", phone_number, {"ip": request.META['REMOTE_ADDR']})
    audit_log("verification_success", phone_number)
    audit_log("verification_failed", phone_number, {"reason": "expired"})

Cost Management
---------------

SMS costs can add up quickly. Implement safeguards:

Spending Limits
^^^^^^^^^^^^^^^

1. Set **spending limits** in your Twilio/Nexmo account
2. Monitor daily/monthly costs
3. Alert when approaching limits

Prevent SMS Spam
^^^^^^^^^^^^^^^^

.. code-block:: python

    from django.core.cache import cache

    def check_global_rate_limit():
        """Prevent application-wide SMS abuse"""
        key = "global_sms_count"
        count = cache.get(key, 0)

        # Max 1000 SMS per hour across the application
        if count >= 1000:
            raise Exception("Global SMS limit reached. Possible abuse.")

        cache.set(key, count + 1, timeout=3600)

International Numbers
^^^^^^^^^^^^^^^^^^^^^

International SMS can be expensive. Consider:

.. code-block:: python

    import phonenumbers

    def is_allowed_country(phone_number):
        """Only allow specific countries"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            country = phonenumbers.region_code_for_number(parsed)
            # Allow only US and Canada
            return country in ['US', 'CA']
        except:
            return False

    class CustomVerificationViewSet(VerificationViewSet):

        @action(detail=False, methods=['POST'])
        def register(self, request):
            phone = request.data.get('phone_number')

            if not is_allowed_country(phone):
                return Response(
                    {"error": "Phone number country not supported"},
                    status=400
                )

            return super().register(request)

Compliance
----------

GDPR / CCPA
^^^^^^^^^^^

If you operate in the EU or California:

1. **Get explicit consent** before sending SMS
2. **Allow users to delete** their phone verification data
3. **Provide data export** functionality
4. **Document data retention** policies

.. code-block:: python

    # Example: GDPR data deletion
    from phone_verify.models import SMSVerification

    def delete_user_phone_data(phone_number):
        """Delete all verification data for a phone number"""
        SMSVerification.objects.filter(phone_number=phone_number).delete()

TCPA (US)
^^^^^^^^^

The Telephone Consumer Protection Act regulates automated messages:

1. Obtain **prior express consent**
2. Provide **opt-out mechanism**
3. **Identify your business** in messages
4. Only send to numbers that opted in

Do Not Call Registries
^^^^^^^^^^^^^^^^^^^^^^^

Check numbers against do-not-call registries if legally required in your jurisdiction.

Security Checklist
------------------

Use this checklist before going to production:

.. code-block:: text

    ☐ Rate limiting implemented (per IP and per phone number)
    ☐ TOKEN_LENGTH >= 6
    ☐ SECURITY_CODE_EXPIRATION_TIME <= 600 (10 minutes)
    ☐ VERIFY_SECURITY_CODE_ONLY_ONCE = True
    ☐ Credentials stored in environment variables or secrets manager
    ☐ Django SECRET_KEY is strong and secret
    ☐ Sandbox backend used in development/test
    ☐ Production backend used in production
    ☐ Phone numbers masked in logs
    ☐ Old verification records regularly deleted
    ☐ Monitoring and alerting set up
    ☐ Spending limits configured with SMS provider
    ☐ User consent obtained before sending SMS
    ☐ Messages include clear branding
    ☐ HTTPS enforced for all API endpoints
    ☐ CSRF protection enabled
    ☐ Audit logging implemented
    ☐ Security testing performed

Reporting Security Issues
--------------------------

If you discover a security vulnerability in ``django-phone-verify``:

1. **Do not** open a public GitHub issue
2. Email the maintainer directly (see README for contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

The maintainer will work with you to address the issue and coordinate disclosure.

Further Reading
---------------

- `OWASP Mobile Security Guide <https://owasp.org/www-project-mobile-security-testing-guide/>`_
- `Twilio Security Best Practices <https://www.twilio.com/docs/usage/security>`_
- `Django Security Documentation <https://docs.djangoproject.com/en/stable/topics/security/>`_
- :doc:`configuration` - Secure configuration options
- :doc:`troubleshooting` - Common security-related issues
