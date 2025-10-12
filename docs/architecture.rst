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
     │                        │                      ├──────────────────►│                    │
     │                        │                      │                   │ 4. Send SMS        │
     │                        │                      │                   ├───────────────────►│
     │                        │                      │                   │                    │
     │                        │                      │ 5. Create Session │                    │
     │                        │                      │    Token (JWT)    │                    │
     │                        │                      │                   │                    │
     │                        │  6. Save to DB       │                   │                    │
     │                        │  (SMSVerification)   │                   │                    │
     │                        │                      │                   │                    │
     │  7. Return             │◄─────────────────────┤                   │                    │
     │     Session Token      │                      │                   │                    │
     │◄───────────────────────┤                      │                   │                    │
     │                        │                      │                   │                    │
     │  8. Receive SMS        │                      │                   │                    │
     │◄─────────────────────────────────────────────────────────────────────────────────────┤
     │                        │                      │                   │                    │

**Details:**

1. User submits their phone number via API/form
2. Application calls ``send_security_code_and_generate_session_token(phone_number)``
3. Backend generates a random security code (e.g., 6-digit number)
4. Backend sends SMS via provider (Twilio/Nexmo)
5. Service generates a JWT session token containing phone number + nonce
6. Creates ``SMSVerification`` record in database with code and token
7. Returns ``session_token`` to user
8. User receives SMS with security code on their phone

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
     │                        │                      │ 3. Validate Token │                 │
     │                        │                      │    (JWT verify)   │                 │
     │                        │                      │                   │                 │
     │                        │                      │ 4. Query DB       │                 │
     │                        │                      ├───────────────────────────────────►│
     │                        │                      │                   │                 │
     │                        │                      │ 5. Check:         │                 │
     │                        │                      │    - Code match?  │                 │
     │                        │                      │    - Expired?     │                 │
     │                        │                      │    - Already used?│                 │
     │                        │                      │                   │                 │
     │                        │  6. Mark as Verified │                   │                 │
     │                        │     (if valid)       ├───────────────────────────────────►│
     │                        │                      │                   │                 │
     │  7. Return Status      │◄─────────────────────┤                   │                 │
     │     (Valid/Invalid)    │                      │                   │                 │
     │◄───────────────────────┤                      │                   │                 │
     │                        │                      │                   │                 │

**Details:**

1. User submits security code + session token from Step 1
2. Application calls ``verify_security_code(phone_number, code, session_token)``
3. Service validates the JWT session token (checks signature, expiration)
4. Queries database for matching ``SMSVerification`` record
5. Backend validates:
   - Does the code match?
   - Has it expired (based on ``SECURITY_CODE_EXPIRATION_TIME``)?
   - Has it already been used (if ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is True)?
6. If valid, marks record as verified in database
7. Returns validation status (``SECURITY_CODE_VALID`` or error)

Key Components
--------------

1. SMSVerification Model
^^^^^^^^^^^^^^^^^^^^^^^^

Stores verification attempts in the database:

.. code-block:: python

    class SMSVerification:
        phone_number          # E.164 format phone number
        session_token         # JWT token for this verification
        security_code         # The code sent via SMS
        is_verified           # Has this been verified?
        created_at            # When was this created?

2. PhoneVerificationService
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Main service class that orchestrates verification:

.. code-block:: python

    class PhoneVerificationService:
        def send_verification(self, context=None)
            # Generates code, sends SMS, returns session token

        def verify(self, security_code, session_token)
            # Validates code and token, returns success/failure

3. Backend Classes
^^^^^^^^^^^^^^^^^^

Abstract interface for SMS providers:

.. code-block:: python

    class BaseBackend:
        def send_sms(number, message)              # Send single SMS
        def send_bulk_sms(numbers, message)        # Send bulk SMS
        def generate_security_code()               # Generate random code
        def generate_session_token(phone_number)   # Generate JWT token
        def validate_security_code(...)            # Validate code

Concrete implementations:

- ``TwilioBackend`` - Uses Twilio API
- ``NexmoBackend`` - Uses Nexmo/Vonage API
- Your custom backends

Security Features
-----------------

JWT Session Tokens
^^^^^^^^^^^^^^^^^^

Session tokens are JWTs (JSON Web Tokens) containing:

- **phone_number**: The phone being verified
- **nonce**: Random value to ensure uniqueness
- **iat**: Issued at timestamp
- **exp**: Expiration timestamp

This prevents:

- ✓ Token reuse across different phones
- ✓ Token tampering (signatures are validated)
- ✓ Replay attacks (nonces ensure uniqueness)

Code Expiration
^^^^^^^^^^^^^^^

Security codes expire after ``SECURITY_CODE_EXPIRATION_TIME`` seconds (recommended: 300-600).

This limits the window for brute-force attacks.

One-Time Use
^^^^^^^^^^^^

When ``VERIFY_SECURITY_CODE_ONLY_ONCE`` is True, codes can only be used once, even if not expired.

This prevents code reuse attacks.

Database Schema
---------------

The ``phone_verify_smsverification`` table structure:

.. code-block:: sql

    CREATE TABLE phone_verify_smsverification (
        id               SERIAL PRIMARY KEY,
        phone_number     VARCHAR(15) NOT NULL,  -- E.164 format
        session_token    TEXT NOT NULL,         -- JWT token
        security_code    VARCHAR(120) NOT NULL, -- Hashed or plain code
        is_verified      BOOLEAN DEFAULT FALSE,
        created_at       TIMESTAMP DEFAULT NOW(),

        CONSTRAINT unique_phone_session
            UNIQUE (phone_number, session_token)
    );

    -- Index for fast lookups during verification
    CREATE INDEX idx_phone_token
        ON phone_verify_smsverification(phone_number, session_token);

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
        'SECURITY_CODE_EXPIRATION_TIME': 600,
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
5. **Custom Validation**: Override ``validate_security_code()`` for custom rules

See :doc:`customization` and :doc:`advanced_examples` for detailed examples.

Performance Considerations
--------------------------

Bottlenecks
^^^^^^^^^^^

1. **SMS API calls** - Typically 100-500ms per SMS
2. **Database writes** - Usually fast (<10ms) but can be a bottleneck at scale
3. **JWT generation/validation** - Minimal overhead (<1ms)

Optimizations
^^^^^^^^^^^^^

1. **Async SMS sending** - Use Celery to send SMS in background
2. **Database connection pooling** - Reuse connections
3. **Caching** - Cache backend instances (they're stateless)
4. **Bulk operations** - Use ``send_bulk_sms()`` for multiple recipients
5. **Cleanup old records** - Periodically delete old ``SMSVerification`` records

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
