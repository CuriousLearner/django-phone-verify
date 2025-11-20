.. _api_reference:

API Reference
=============

This page provides a complete reference for the core APIs, services, and models in ``django-phone-verify``.

Services
--------

PhoneVerificationService
^^^^^^^^^^^^^^^^^^^^^^^^

.. py:class:: phone_verify.services.PhoneVerificationService(phone_number, backend=None)

   Main service class for sending and managing phone verification messages.

   :param str phone_number: The phone number to verify (E.164 format recommended)
   :param backend: Optional backend instance. If None, uses the configured backend from settings
   :type backend: BaseBackend or None

   **Methods:**

   .. py:method:: send_verification(number, security_code, context=None)

      Send a verification SMS to the specified phone number.

      :param str number: Recipient phone number
      :param str security_code: The generated security code to send
      :param dict context: Optional context for custom message formatting (e.g., ``{"username": "John"}``)
      :raises: Backend-specific exception (e.g., ``TwilioRestException``)

      **Example:**

      .. code-block:: python

         from phone_verify.services import PhoneVerificationService

         service = PhoneVerificationService(phone_number="+1234567890")
         service.send_verification(
             number="+1234567890",
             security_code="123456",
             context={"username": "Alice"}
         )

.. py:function:: phone_verify.services.send_security_code_and_generate_session_token(phone_number)

   High-level function that generates a security code, creates a session token, and sends the SMS.

   :param str phone_number: The phone number to send the code to
   :return: The generated session token (JWT)
   :rtype: str

   **Example:**

   .. code-block:: python

      from phone_verify.services import send_security_code_and_generate_session_token

      session_token = send_security_code_and_generate_session_token("+1234567890")
      # Returns: "eyJ0eXAiOiJKV1QiLCJhbGc..."

Backends
--------

BaseBackend
^^^^^^^^^^^

.. py:class:: phone_verify.backends.base.BaseBackend(**settings)

   Abstract base class for all SMS backends. Extend this to create custom backends.

   **Class Attributes:**

   - ``SECURITY_CODE_VALID = 0`` - Code is valid and verified
   - ``SECURITY_CODE_INVALID = 1`` - Code doesn't exist or is incorrect
   - ``SECURITY_CODE_EXPIRED = 2`` - Code has expired
   - ``SECURITY_CODE_VERIFIED = 3`` - Code already used (when ``VERIFY_SECURITY_CODE_ONLY_ONCE=True``)
   - ``SESSION_TOKEN_INVALID = 4`` - Session token doesn't match

   **Abstract Methods (must be implemented):**

   .. py:method:: send_sms(number, message)
      :abstractmethod:

      Send a single SMS message.

      :param str number: Recipient phone number
      :param str message: Message content

   .. py:method:: send_bulk_sms(numbers, message)
      :abstractmethod:

      Send an SMS to multiple recipients.

      :param list numbers: List of recipient phone numbers
      :param str message: Message content

   **Concrete Methods:**

   .. py:classmethod:: generate_security_code()

      Generate a random numeric security code based on ``TOKEN_LENGTH`` setting.

      :return: Random numeric string (e.g., "123456")
      :rtype: str

   .. py:classmethod:: generate_session_token(phone_number)

      Generate a unique JWT session token for the phone number.

      :param str phone_number: Phone number to encode
      :return: JWT token
      :rtype: str

   .. py:method:: create_security_code_and_session_token(number)

      Create a security code and session token, storing them in the database.

      :param str number: Phone number
      :return: Tuple of (security_code, session_token)
      :rtype: tuple

   .. py:method:: validate_security_code(security_code, phone_number, session_token)

      Validate a security code for a phone number.

      :param str security_code: The code to validate
      :param str phone_number: Phone number to verify
      :param str session_token: Session token from registration
      :return: Tuple of (SMSVerification object or None, status code)
      :rtype: tuple

   .. py:method:: generate_message(security_code, context=None)

      Optional method to customize message generation. Return None to use default.

      :param str security_code: The generated code
      :param dict context: Optional runtime context
      :return: Custom message string or None
      :rtype: str or None

      **Example:**

      .. code-block:: python

         def generate_message(self, security_code, context=None):
             username = context.get("username", "User") if context else "User"
             return f"Hi {username}, your OTP is {security_code}."

TwilioBackend
^^^^^^^^^^^^^

.. py:class:: phone_verify.backends.twilio.TwilioBackend(**options)

   Twilio SMS backend implementation.

   **Required OPTIONS:**

   - ``SID``: Twilio Account SID
   - ``SECRET``: Twilio Auth Token
   - ``FROM``: Twilio phone number (E.164 format)

   **Example Configuration:**

   .. code-block:: python

      PHONE_VERIFICATION = {
          "BACKEND": "phone_verify.backends.twilio.TwilioBackend",
          "OPTIONS": {
              "SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
              "SECRET": "your_auth_token",
              "FROM": "+15551234567",
          },
          ...
      }

NexmoBackend
^^^^^^^^^^^^

.. py:class:: phone_verify.backends.nexmo.NexmoBackend(**options)

   Nexmo (Vonage) SMS backend implementation.

   **Required OPTIONS:**

   - ``KEY``: Nexmo API Key
   - ``SECRET``: Nexmo API Secret
   - ``FROM``: Sender ID or phone number

   **Example Configuration:**

   .. code-block:: python

      PHONE_VERIFICATION = {
          "BACKEND": "phone_verify.backends.nexmo.NexmoBackend",
          "OPTIONS": {
              "KEY": "your_api_key",
              "SECRET": "your_api_secret",
              "FROM": "YourApp",
          },
          ...
      }

Models
------

SMSVerification
^^^^^^^^^^^^^^^

.. py:class:: phone_verify.models.SMSVerification

   Database model for storing verification attempts.

   **Fields:**

   - ``id`` (UUIDField): Primary key
   - ``phone_number`` (PhoneNumberField): Phone number being verified
   - ``security_code`` (CharField): The verification code sent
   - ``session_token`` (CharField): JWT token for this verification session
   - ``is_verified`` (BooleanField): Whether the code has been successfully verified
   - ``failed_attempts`` (PositiveIntegerField): Number of failed verification attempts (default: 0)
   - ``created_at`` (DateTimeField): When the verification was created
   - ``modified_at`` (DateTimeField): Last modification time

   **Properties:**

   .. py:attribute:: is_expired

      Returns ``True`` if the security code has expired based on the ``SECURITY_CODE_EXPIRATION_SECONDS`` setting.

      :return: Whether the code is expired
      :rtype: bool

      **Example:**

      .. code-block:: python

         verification = SMSVerification.objects.get(session_token=token)
         if verification.is_expired:
             print("Code has expired")

   **Constraints:**

   - Unique together: (``security_code``, ``phone_number``, ``session_token``)
   - Ordered by: ``-modified_at`` (newest first)

   **Example Query:**

   .. code-block:: python

      from phone_verify.models import SMSVerification

      # Find unverified codes for a phone number
      pending = SMSVerification.objects.filter(
          phone_number="+1234567890",
          is_verified=False
      )

      # Check if a verification has expired
      verification = SMSVerification.objects.first()
      if verification and verification.is_expired:
          print("Verification has expired")

Serializers
-----------

PhoneSerializer
^^^^^^^^^^^^^^^

.. py:class:: phone_verify.serializers.PhoneSerializer

   Simple serializer for phone number input.

   **Fields:**

   - ``phone_number`` (PhoneNumberField): Required phone number field

   **Usage:**

   .. code-block:: python

      serializer = PhoneSerializer(data={"phone_number": "+1234567890"})
      if serializer.is_valid():
          phone = serializer.validated_data["phone_number"]

SMSVerificationSerializer
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:class:: phone_verify.serializers.SMSVerificationSerializer

   Serializer for verifying a security code.

   **Fields:**

   - ``phone_number`` (PhoneNumberField): Phone number to verify
   - ``security_code`` (CharField): The code received via SMS
   - ``session_token`` (CharField): Session token from registration

   **Validation:**

   Automatically validates the security code against the backend and raises appropriate errors:

   - "Security code is not valid"
   - "Session Token mis-match"
   - "Security code has expired"
   - "Security code is already verified"

   **Usage:**

   .. code-block:: python

      serializer = SMSVerificationSerializer(data={
          "phone_number": "+1234567890",
          "security_code": "123456",
          "session_token": "eyJ0eXAi..."
      })
      serializer.is_valid(raise_exception=True)

ViewSets
--------

VerificationViewSet
^^^^^^^^^^^^^^^^^^^

.. py:class:: phone_verify.api.VerificationViewSet

   DRF ViewSet with two main actions for phone verification flow.

   **Actions:**

   .. py:method:: register(request)

      **POST** ``/api/phone/register``

      Send a security code to a phone number.

      **Request Body:**

      .. code-block:: json

         {
             "phone_number": "+1234567890"
         }

      **Response:**

      .. code-block:: json

         {
             "session_token": "eyJ0eXAiOiJKV1QiLCJ..."
         }

   .. py:method:: verify(request)

      **POST** ``/api/phone/verify``

      Verify a security code.

      **Request Body:**

      .. code-block:: json

         {
             "phone_number": "+1234567890",
             "security_code": "123456",
             "session_token": "eyJ0eXAiOiJKV1QiLCJ..."
         }

      **Response:**

      .. code-block:: json

         {
             "message": "Security code is valid."
         }

   **Extending:**

   You can extend this ViewSet to add custom actions:

   .. code-block:: python

      from phone_verify.api import VerificationViewSet

      class CustomVerificationViewSet(VerificationViewSet):
          @action(detail=False, methods=['POST'])
          def verify_and_login(self, request):
              # Custom logic here
              pass

Django Admin Interface
----------------------

SMSVerificationAdmin
^^^^^^^^^^^^^^^^^^^^

The Django admin interface provides an intuitive way to manage and monitor phone verifications.

**Features:**

- **List Display**: Shows ID, security code, phone number, verification status, validity status, failed attempts, and creation date
- **Is Valid**: Boolean indicator using Django's standard icons - green checkmark when valid, red X when expired
- **Search**: Search by phone number
- **Filters**: Filter by verification status and creation date
- **Read-only Fields**: All fields are read-only to prevent accidental modifications

**Accessing the Admin:**

1. Navigate to Django admin: ``/admin/``
2. Click on "SMS Verifications" under the "Phone Verify" section
3. View all verification records with their validity status

**Example View:**

The admin list will show entries like:

- **ID**: 550e8400-e29b-41d4-a716-446655440000
- **Security Code**: 123456
- **Phone Number**: +1234567890
- **Is Verified**: ✓ (green checkmark)
- **Is Valid**: ✓ (green checkmark - not expired) or ✗ (red X - expired)
- **Failed Attempts**: 0
- **Created At**: 2025-10-19 14:30:00

Management Commands
-------------------

cleanup_phone_verifications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Django management command to clean up old SMS verification records from the database.

**Usage:**

.. code-block:: bash

   # Delete records older than the default retention period (30 days or RECORD_RETENTION_DAYS setting)
   python manage.py cleanup_phone_verifications

   # Delete records older than a custom number of days
   python manage.py cleanup_phone_verifications --days 7

   # Dry-run mode: preview what would be deleted without actually deleting
   python manage.py cleanup_phone_verifications --dry-run

   # Combine options
   python manage.py cleanup_phone_verifications --days 14 --dry-run

**Options:**

- ``--days N``: Number of days to retain records (overrides ``RECORD_RETENTION_DAYS`` setting)
- ``--dry-run``: Show what would be deleted without actually deleting anything

**Configuration:**

Add ``RECORD_RETENTION_DAYS`` to your ``PHONE_VERIFICATION`` settings to set the default retention period:

.. code-block:: python

   PHONE_VERIFICATION = {
       ...
       'RECORD_RETENTION_DAYS': 30,  # Keep records for 30 days (default)
   }

**Scheduling:**

For production use, schedule this command to run periodically using cron, Celery Beat, or your preferred task scheduler:

.. code-block:: bash

   # Example crontab entry (runs daily at 2 AM)
   0 2 * * * /path/to/python /path/to/manage.py cleanup_phone_verifications

**Example Output:**

.. code-block:: text

   Successfully deleted 42 verification record(s) older than 30 days

Or for dry-run mode:

.. code-block:: text

   DRY RUN: Would delete 42 verification record(s) older than 30 days
   Records that would be deleted:
     - +1234567890 (created: 2025-09-15 10:23:45)
     - +1234567891 (created: 2025-09-14 08:15:30)
     ... and 40 more
