.. _architecture:

Architecture & Flow
===================

This document explains how ``django-phone-verify`` works internally and how the verification flow operates.

System Architecture
-------------------

``django-phone-verify`` uses a layered architecture:

.. code-block:: text

    ┌─────────────────────────────────────────────────────────┐
    │                     Your Application                     │
    │  (Views, ViewSets, Forms, Custom Logic)                 │
    └────────────────────┬────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Phone Verify API Layer                      │
    │  • VerificationViewSet (DRF)                            │
    │  • PhoneSerializer, SMSVerificationSerializer           │
    └────────────────────┬────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Service Layer                               │
    │  • PhoneVerificationService                             │
    │  • send_security_code_and_generate_session_token()      │
    │  • verify_security_code()                               │
    └────────────────────┬────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Backend Layer                               │
    │  • BaseBackend (abstract)                               │
    │  • TwilioBackend, NexmoBackend                          │
    │  • Your Custom Backends                                 │
    └────────────────────┬────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Data Layer                                  │
    │  • SMSVerification Model (Database)                     │
    │  • Stores: phone_number, security_code,                 │
    │    session_token, created_at, is_verified               │
    └─────────────────────────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │              External SMS Providers                      │
    │  • Twilio API                                           │
    │  • Nexmo/Vonage API                                     │
    │  • Your Custom Provider                                 │
    └─────────────────────────────────────────────────────────┘


Verification Flow
-----------------

The phone verification process happens in two main steps:

Step 1: Request Verification Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

    User                 Application           Phone Verify          Backend           SMS Provider
     │                        │                      │                   │                    │
     │  1. Submit Phone       │                      │                   │                    │
     ├──────────────────────►│                      │                   │                    │
     │                        │  2. Call Service     │                   │                    │
     │                        ├────────────────────►│                   │                    │
     │                        │                      │ 3. Generate Code  │                    │
     │                        │                      │    + Session      │                    │
     │                        │                      │    Token          │                    │
     │                        │                      ├──────────────────►│                    │
     │                        │                      │                   │                    │
     │                        │                      │ 4. Replace any    │                    │
     │                        │                      │    prior row and  │                    │
     │                        │                      │    save to DB     │                    │
     │                        │                      │    (SMSVerification)                   │
     │                        │                      │                   │                    │
     │                        │                      │                   │ 5. Send SMS        │
     │                        │                      │                   ├───────────────────►│
     │                        │                      │                   │                    │
     │  6. Return             │◄─────────────────────┤                   │                    │
     │     Session Token      │                      │                   │                    │
     │◄───────────────────────┤                      │                   │                    │
     │                        │                      │                   │                    │
     │  7. Receive SMS        │                      │                   │                    │
     │◄─────────────────────────────────────────────────────────────────────────────────────┤
     │                        │                      │                   │                    │

**Details:**

1. User submits their phone number via API/form
2. Application calls ``send_security_code_and_generate_session_token(phone_number)``
3. ``create_security_code_and_session_token()`` generates a random security code
   (e.g., 6-digit number) and a session token for this device
4. Any existing ``SMSVerification`` row for that phone number is deleted, then a fresh one is
   created holding the code and token. The record is written **before** the SMS goes out, so a
   provider failure still leaves a usable record
5. ``PhoneVerificationService.send_verification()`` formats the message and hands it to the
   backend's ``send_sms()``. Errors matching the backend's ``exception_class`` are logged and
   swallowed, so a provider outage does not surface as a 500
6. Returns ``session_token`` to the caller
7. User receives SMS with security code on their phone

Step 2: Verify Security Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

    User                 Application           Phone Verify          Backend           Database
     │                        │                      │                   │                 │
     │  1. Submit Code +      │                      │                   │                 │
     │     Session Token      │                      │                   │                 │
     ├──────────────────────►│                      │                   │                 │
     │                        │  2. Call Service     │                   │                 │
     │                        ├────────────────────►│                   │                 │
     │                        │                      │ 3. Look up row by │                 │
     │                        │                      │    (phone_number, │                 │
     │                        │                      │     session_token)│                 │
     │                        │                      ├───────────────────────────────────►│
     │                        │                      │                   │                 │
     │                        │                      │ 4. Check:         │                 │
     │                        │                      │    - Too many     │                 │
     │                        │                      │      attempts?    │                 │
     │                        │                      │    - Code match?  │                 │
     │                        │                      │    - Expired?     │                 │
     │                        │                      │    - Already used?│                 │
     │                        │                      │                   │                 │
     │                        │  5. Mark as Verified │                   │                 │
     │                        │     (if valid)       ├───────────────────────────────────►│
     │                        │                      │                   │                 │
     │  6. Return Status      │◄─────────────────────┤                   │                 │
     │     (Valid/Invalid)    │                      │                   │                 │
     │◄───────────────────────┤                      │                   │                 │
     │                        │                      │                   │                 │

**Details:**

1. User submits security code + session token from Step 1
2. Application calls ``verify_security_code(phone_number, code, session_token)``
3. The backend queries for the ``SMSVerification`` row matching both ``phone_number`` and
   ``session_token``. The session token is used as an opaque lookup key here; it is never
   decoded, and no signature check is performed. No matching row means
   ``SESSION_TOKEN_INVALID``
4. Backend validates, in order:

   - Has ``failed_attempts`` reached ``MAX_FAILED_ATTEMPTS``? If so the record is locked and
     returns ``SECURITY_CODE_TOO_MANY_ATTEMPTS`` without looking at the code
   - Does the code match? A mismatch increments ``failed_attempts``
   - Has it expired (based on ``SECURITY_CODE_EXPIRATION_SECONDS``)?
   - Has it already been used (if ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is True)?

   Expired and already-used outcomes also increment ``failed_attempts``
5. If valid, marks the record as verified and resets ``failed_attempts`` to ``0``
6. Returns a ``(verification, status)`` tuple where ``status`` is ``SECURITY_CODE_VALID`` or
   one of the error constants

Key Components
--------------

1. SMSVerification Model
^^^^^^^^^^^^^^^^^^^^^^^^

Stores verification attempts in the database:

.. code-block:: python

    class SMSVerification:
        phone_number          # E.164 format phone number
        session_token         # Opaque per-device token for this verification
        security_code         # The code sent via SMS
        is_verified           # Has this been verified?
        failed_attempts       # Wrong/expired/reused code count, for lockout
        created_at            # When was this created?

2. PhoneVerificationService
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Main service class that orchestrates verification:

.. code-block:: python

    class PhoneVerificationService:
        def send_verification(self, number, security_code, context=None):
            """Formats the message and sends the SMS via the backend."""
            ...

Sending a code and generating a session token is done through the
``send_security_code_and_generate_session_token()`` service function, which
delegates to the backend's ``create_security_code_and_session_token()`` and
``send_sms()``. Verification is done through the ``verify_security_code()``
service function, or the ``SMSVerificationSerializer``; both of those delegate
to the backend's ``validate_security_code()``. The service class itself has no
``verify`` method.

3. Backend Classes
^^^^^^^^^^^^^^^^^^

Abstract interface for SMS providers:

.. code-block:: python

    class BaseBackend:
        def send_sms(number, message): ...              # ABSTRACT: the only method
                                                        # a custom backend must implement
        def send_bulk_sms(numbers, message): ...        # Concrete: loops over send_sms
        def generate_security_code(): ...               # Generate random code
        def generate_session_token(phone_number): ...   # Generate per-device token
        def _should_bypass_code_check(security_code):   # Sandbox hook, default False
            ...
        def validate_security_code(                     # Validate code
            security_code, phone_number, session_token
        ): ...

Concrete implementations:

- ``TwilioBackend`` - Uses Twilio API
- ``NexmoBackend`` - Uses Nexmo/Vonage API
- Your custom backends

Security Features
-----------------

Session Tokens
^^^^^^^^^^^^^^

``generate_session_token()`` builds the token with ``jwt.encode()`` over a payload of:

- **phone_number**: The phone being verified
- **nonce**: Random value, so two tokens for the same number never collide

Understand what this does and does not give you:

- It is stored verbatim on the ``SMSVerification`` row and matched as a plain string at verify
  time. The package calls ``jwt.encode()`` and never ``jwt.decode()``, so the token is an
  opaque signed string used as a lookup key, not a set of claims the library reads back
- Because the signature is never checked, a tampered token does not fail validation, it simply
  fails to match any stored row and returns ``SESSION_TOKEN_INVALID``
- The payload carries no ``iat`` or ``exp``, and the token has no independent expiry. What
  expires is the ``SMSVerification`` record, governed by
  ``SECURITY_CODE_EXPIRATION_SECONDS`` and measured from the row's ``created_at``
- It is a **bearer value**. Anyone holding it can attempt the verify step for that phone
  number, so treat it like a short-lived credential: send it over HTTPS only, and keep it out
  of URLs, logs and client-side storage that outlives the flow

What it does buy you is binding: the verify request has to come from whoever received the
register response, so a code guessed or intercepted in isolation is not enough.

Code Expiration
^^^^^^^^^^^^^^^

Security codes expire after ``SECURITY_CODE_EXPIRATION_SECONDS`` seconds (recommended: 300-600).

This limits the window for brute-force attacks.

Failed Attempt Lockout
^^^^^^^^^^^^^^^^^^^^^^

Each ``SMSVerification`` row tracks ``failed_attempts``. Once it reaches
``MAX_FAILED_ATTEMPTS`` (default ``5``) the record stops accepting codes entirely and returns
``SECURITY_CODE_TOO_MANY_ATTEMPTS``; the user must request a new code. The counter is
incremented atomically with an ``F()`` expression, so concurrent guesses cannot race past the
limit, and it resets on a successful verification.

This caps guesses against a single code. It is per-record, not per-IP or per-endpoint, so it
does not replace request rate limiting. See :doc:`security`.

One-Time Use
^^^^^^^^^^^^

When ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is True, codes can only be used once, even if not expired.

This prevents code reuse attacks.

Database Schema
---------------

The ``sms_verification`` table structure:

.. code-block:: sql

    CREATE TABLE sms_verification (
        id               UUID PRIMARY KEY,        -- uuid4, not auto-increment
        security_code    VARCHAR(120) NOT NULL,   -- plain code sent via SMS
        phone_number     VARCHAR(128) NOT NULL,   -- E.164 format
        session_token    VARCHAR(500) NOT NULL,   -- opaque per-device token
        is_verified      BOOLEAN DEFAULT FALSE,
        failed_attempts  INTEGER DEFAULT 0,       -- brute-force counter
        created_at       TIMESTAMP NOT NULL,
        modified_at      TIMESTAMP NOT NULL,

        CONSTRAINT unique_code_phone_session
            UNIQUE (security_code, phone_number, session_token)
    );

Configuration Flow
------------------

Settings are loaded from ``PHONE_VERIFICATION`` in ``settings.py``:

.. code-block:: python

    PHONE_VERIFICATION = {
        'BACKEND': 'phone_verify.backends.twilio.TwilioBackend',
        'OPTIONS': { ... },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Code: {security_code}',
        'APP_NAME': 'MyApp',
        'SECURITY_CODE_EXPIRATION_SECONDS': 600,
        'VERIFY_SECURITY_CODE_ONLY_ONCE': True,
    }

When the service is initialized:

1. Backend class is imported (``TwilioBackend``)
2. Backend is instantiated with ``OPTIONS``
3. Settings are validated for required fields
4. Backend client (Twilio SDK) is initialized

Extension Points
----------------

You can extend ``django-phone-verify`` at multiple levels:

1. **Custom Backends**: Implement ``BaseBackend`` for new SMS providers
2. **Custom Viewsets**: Extend ``VerificationViewSet`` for custom API logic
3. **Custom Services**: Wrap ``PhoneVerificationService`` for custom flows
4. **Custom Messages**: Override ``generate_message()`` for dynamic messages
5. **Sandbox Bypass**: Override ``_should_bypass_code_check()`` to accept a fixed test code
   while keeping expiry, one-time use and the failed-attempt lockout intact. Prefer this over
   replacing ``validate_security_code()``, which is where all three are enforced

See :doc:`customization` and :doc:`advanced_examples` for detailed examples.

Performance Considerations
--------------------------

Bottlenecks
^^^^^^^^^^^

1. **SMS API calls** - Typically 100-500ms per SMS
2. **Database writes** - Usually fast (<10ms) but can be a bottleneck at scale
3. **Session token generation** - Minimal overhead (<1ms); there is no decode step at verify time

Optimizations
^^^^^^^^^^^^^

1. **Async SMS sending** - Use Celery to send SMS in background
2. **Database connection pooling** - Reuse connections
3. **Caching** - Cache backend instances (they're stateless)
4. **Bulk operations** - Use ``send_bulk_sms()`` for multiple recipients
5. **Cleanup old records** - Run the shipped ``cleanup_phone_verifications`` management
   command periodically to delete old ``SMSVerification`` rows

Monitoring & Observability
---------------------------

Key Metrics to Track
^^^^^^^^^^^^^^^^^^^^

- **SMS success rate** - % of SMS successfully delivered
- **Verification success rate** - % of codes successfully verified
- **Time to verify** - How long users take from code request to verification
- **Code expiration rate** - % of codes that expire before being used
- **Failed attempts** - Rate of failed verification attempts (indicates brute force?)
- **SMS costs** - Total spending on SMS (track by provider)

Logging Best Practices
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Enable debug logging
    LOGGING = {
        'version': 1,
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': '/var/log/django/phone_verify.log',
            },
        },
        'loggers': {
            'phone_verify': {
                'handlers': ['file'],
                'level': 'INFO',
            },
        },
    }

Log important events:

- SMS sent successfully
- SMS failed to send (with error)
- Verification attempts (success/failure)
- Rate limit violations
- Security code generation

**Do not log**: Phone numbers or security codes in plain text (GDPR/privacy).

Further Reading
---------------

- :doc:`getting_started` - Installation and configuration
- :doc:`integration` - How to integrate into your app
- :doc:`customization` - Writing custom backends
- :doc:`security` - Security best practices
- :doc:`api_reference` - Complete API documentation
