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
   - ``created_at`` (DateTimeField): When the verification was created
   - ``modified_at`` (DateTimeField): Last modification time

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
