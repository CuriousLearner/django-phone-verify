.. _advanced_examples:

Advanced Examples
=================

This guide provides real-world examples and use cases for ``django-phone-verify`` beyond basic registration.

Two-Factor Authentication (2FA)
--------------------------------

Use phone verification as a second authentication factor for login.

Backend Implementation
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # myapp/views.py
    from django.contrib.auth import authenticate
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from rest_framework import status
    from phone_verify.api import VerificationViewSet
    from phone_verify.services import send_security_code_and_generate_session_token

    class TwoFactorViewSet(VerificationViewSet):

        @action(detail=False, methods=['POST'])
        def login_step1(self, request):
            """Step 1: Verify username/password"""
            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(username=username, password=password)

            if user is None:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not hasattr(user, 'phone_number') or not user.phone_number:
                return Response(
                    {"error": "Phone number not configured for this account"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Send verification code
            session_token = send_security_code_and_generate_session_token(
                str(user.phone_number)
            )

            # Store user ID in session token (for step 2)
            request.session['pending_2fa_user_id'] = user.id

            return Response({
                "message": "Verification code sent",
                "session_token": session_token,
                "phone_number": str(user.phone_number)
            })

        @action(detail=False, methods=['POST'])
        def login_step2(self, request):
            """Step 2: Verify phone code and complete login"""
            from phone_verify.serializers import SMSVerificationSerializer
            from rest_framework.authtoken.models import Token

            # Verify the code
            serializer = SMSVerificationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Get user from session
            user_id = request.session.get('pending_2fa_user_id')
            if not user_id:
                return Response(
                    {"error": "Invalid session"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.get(id=user_id)

            # Create auth token
            token, _ = Token.objects.get_or_create(user=user)

            # Clean up session
            del request.session['pending_2fa_user_id']

            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username
            })

Frontend Flow
^^^^^^^^^^^^^

.. code-block:: javascript

    // Step 1: Username/Password
    async function loginStep1(username, password) {
        const response = await fetch('/api/auth/login_step1', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });

        const data = await response.json();

        if (response.ok) {
            // Store session token for step 2
            sessionStorage.setItem('2fa_session_token', data.session_token);
            sessionStorage.setItem('2fa_phone', data.phone_number);
            return true;
        }
        return false;
    }

    // Step 2: Phone Verification
    async function loginStep2(securityCode) {
        const sessionToken = sessionStorage.getItem('2fa_session_token');
        const phoneNumber = sessionStorage.getItem('2fa_phone');

        const response = await fetch('/api/auth/login_step2', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                phone_number: phoneNumber,
                security_code: securityCode,
                session_token: sessionToken
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Store auth token
            localStorage.setItem('auth_token', data.token);
            sessionStorage.removeItem('2fa_session_token');
            sessionStorage.removeItem('2fa_phone');
            return true;
        }
        return false;
    }

Account Recovery / Password Reset
----------------------------------

Verify phone number before allowing password reset.

Implementation
^^^^^^^^^^^^^^

.. code-block:: python

    # myapp/views.py
    from django.contrib.auth import get_user_model
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from phone_verify.api import VerificationViewSet
    from phone_verify.services import send_security_code_and_generate_session_token

    User = get_user_model()

    class PasswordResetViewSet(VerificationViewSet):

        @action(detail=False, methods=['POST'])
        def request_reset(self, request):
            """Step 1: Request password reset via phone"""
            phone_number = request.data.get('phone_number')

            # Find user by phone (don't reveal if exists)
            try:
                user = User.objects.get(phone_number=phone_number)
                session_token = send_security_code_and_generate_session_token(phone_number)
                request.session['reset_user_id'] = user.id
            except User.DoesNotExist:
                # Still return success to avoid enumeration
                session_token = "fake_token"

            return Response({
                "message": "If this phone number is registered, a code was sent",
                "session_token": session_token
            })

        @action(detail=False, methods=['POST'])
        def verify_and_reset(self, request):
            """Step 2: Verify code and set new password"""
            from phone_verify.serializers import SMSVerificationSerializer

            # Verify code
            serializer = SMSVerificationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Get user
            user_id = request.session.get('reset_user_id')
            if not user_id:
                return Response(
                    {"error": "Invalid session"},
                    status=400
                )

            user = User.objects.get(id=user_id)

            # Set new password
            new_password = request.data.get('new_password')
            if not new_password or len(new_password) < 8:
                return Response(
                    {"error": "Password must be at least 8 characters"},
                    status=400
                )

            user.set_password(new_password)
            user.save()

            del request.session['reset_user_id']

            return Response({"message": "Password reset successful"})

Marketing Opt-In / SMS Campaigns
---------------------------------

Verify phone numbers before adding to marketing lists.

Implementation
^^^^^^^^^^^^^^

.. code-block:: python

    # myapp/models.py
    from django.db import models

    class MarketingSubscriber(models.Model):
        phone_number = models.CharField(max_length=20, unique=True)
        opted_in_at = models.DateTimeField(auto_now_add=True)
        is_verified = models.BooleanField(default=False)
        preferences = models.JSONField(default=dict)

        def __str__(self):
            return self.phone_number

.. code-block:: python

    # myapp/views.py
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from phone_verify.api import VerificationViewSet
    from phone_verify.services import send_security_code_and_generate_session_token
    from .models import MarketingSubscriber

    class MarketingOptInViewSet(VerificationViewSet):

        @action(detail=False, methods=['POST'])
        def subscribe(self, request):
            """Step 1: Request to subscribe to marketing"""
            phone_number = request.data.get('phone_number')
            preferences = request.data.get('preferences', {})

            # Create or update subscriber (unverified)
            subscriber, created = MarketingSubscriber.objects.get_or_create(
                phone_number=phone_number,
                defaults={'preferences': preferences}
            )

            if not created:
                subscriber.preferences = preferences
                subscriber.save()

            # Send verification
            session_token = send_security_code_and_generate_session_token(phone_number)

            return Response({
                "message": "Please verify your phone number",
                "session_token": session_token
            })

        @action(detail=False, methods=['POST'])
        def confirm_subscription(self, request):
            """Step 2: Verify code and complete subscription"""
            from phone_verify.serializers import SMSVerificationSerializer

            # Verify code
            serializer = SMSVerificationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            phone_number = serializer.validated_data['phone_number']

            # Mark subscriber as verified
            subscriber = MarketingSubscriber.objects.get(phone_number=phone_number)
            subscriber.is_verified = True
            subscriber.save()

            return Response({
                "message": "Subscription confirmed!",
                "preferences": subscriber.preferences
            })

        @action(detail=False, methods=['POST'])
        def unsubscribe(self, request):
            """Unsubscribe from marketing"""
            phone_number = request.data.get('phone_number')

            MarketingSubscriber.objects.filter(phone_number=phone_number).delete()

            return Response({"message": "Unsubscribed successfully"})

Multi-Tenant Application
-------------------------

Different verification settings per tenant/organization.

Implementation
^^^^^^^^^^^^^^

.. code-block:: python

    # myapp/models.py
    from django.db import models

    class Organization(models.Model):
        name = models.CharField(max_length=255)
        twilio_sid = models.CharField(max_length=255)
        twilio_secret = models.CharField(max_length=255)
        twilio_from_number = models.CharField(max_length=20)
        sms_message_template = models.TextField(
            default="Your {app} code is {security_code}"
        )
        token_length = models.IntegerField(default=6)
        code_expiration_seconds = models.IntegerField(default=600)

.. code-block:: python

    # myapp/backends.py
    from phone_verify.backends.twilio import TwilioBackend

    class MultiTenantBackend(TwilioBackend):
        def __init__(self, organization, **options):
            self.organization = organization

            # Use organization-specific settings
            options = {
                'SID': organization.twilio_sid,
                'SECRET': organization.twilio_secret,
                'FROM': organization.twilio_from_number,
            }

            super().__init__(**options)

        def generate_message(self, security_code, context=None):
            return self.organization.sms_message_template.format(
                app=self.organization.name,
                security_code=security_code,
                **(context or {})
            )

.. code-block:: python

    # myapp/services.py
    from phone_verify.services import PhoneVerificationService
    from .backends import MultiTenantBackend
    from .models import Organization

    def send_verification_for_org(organization_id, phone_number):
        """Send verification using organization-specific settings"""
        org = Organization.objects.get(id=organization_id)

        backend = MultiTenantBackend(organization=org)
        service = PhoneVerificationService(
            phone_number=phone_number,
            backend=backend
        )

        security_code, session_token = backend.create_security_code_and_session_token(
            phone_number
        )

        service.send_verification(phone_number, security_code)

        return session_token

Async/Celery Integration
-------------------------

Send SMS asynchronously to improve API response times.

Implementation
^^^^^^^^^^^^^^

.. code-block:: python

    # myapp/tasks.py
    from celery import shared_task
    from phone_verify.services import PhoneVerificationService
    from phone_verify.backends import get_sms_backend

    @shared_task
    def send_verification_async(phone_number):
        """Send verification code asynchronously"""
        backend = get_sms_backend(phone_number=phone_number)

        security_code, session_token = backend.create_security_code_and_session_token(
            phone_number
        )

        service = PhoneVerificationService(phone_number=phone_number)

        try:
            service.send_verification(phone_number, security_code)
        except Exception as e:
            # Log error but don't fail - user can retry
            import logging
            logging.error(f"Failed to send SMS to {phone_number}: {e}")

        return session_token

.. code-block:: python

    # myapp/views.py
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from phone_verify.api import VerificationViewSet
    from .tasks import send_verification_async

    class AsyncVerificationViewSet(VerificationViewSet):

        @action(detail=False, methods=['POST'])
        def register(self, request):
            """Send verification code asynchronously"""
            phone_number = request.data.get('phone_number')

            # Validate phone number first
            from phone_verify.serializers import PhoneSerializer
            serializer = PhoneSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Send async
            task = send_verification_async.delay(str(serializer.validated_data['phone_number']))

            # Return immediately
            return Response({
                "message": "Verification code will be sent shortly",
                "task_id": task.id  # Optional: for checking status
            })

Custom Message Per Context
---------------------------

Send different messages based on context (registration, login, etc.).

Implementation
^^^^^^^^^^^^^^

.. code-block:: python

    # myapp/backends.py
    from phone_verify.backends.twilio import TwilioBackend

    class ContextAwareBackend(TwilioBackend):
        MESSAGE_TEMPLATES = {
            'registration': 'Welcome to {app}! Your registration code is {security_code}.',
            'login': 'Your {app} login code is {security_code}. Valid for 5 minutes.',
            'password_reset': 'Your {app} password reset code is {security_code}. Did not request this? Ignore.',
            '2fa': '{app} security verification: {security_code}',
            'default': 'Your {app} verification code is {security_code}.',
        }

        def generate_message(self, security_code, context=None):
            context_type = context.get('type', 'default') if context else 'default'
            template = self.MESSAGE_TEMPLATES.get(context_type, self.MESSAGE_TEMPLATES['default'])

            from django.conf import settings
            return template.format(
                app=settings.PHONE_VERIFICATION['APP_NAME'],
                security_code=security_code,
                **(context or {})
            )

.. code-block:: python

    # Usage in views
    from phone_verify.services import PhoneVerificationService

    def send_registration_code(phone_number, username):
        service = PhoneVerificationService(phone_number)
        backend = service.backend

        security_code, session_token = backend.create_security_code_and_session_token(
            phone_number
        )

        service.send_verification(
            phone_number,
            security_code,
            context={'type': 'registration', 'username': username}
        )

        return session_token

Fallback SMS Provider
----------------------

Use multiple SMS providers with automatic fallback.

Implementation
^^^^^^^^^^^^^^

.. code-block:: python

    # myapp/backends.py
    from phone_verify.backends.base import BaseBackend
    from phone_verify.backends.twilio import TwilioBackend
    from phone_verify.backends.nexmo import NexmoBackend
    import logging

    logger = logging.getLogger(__name__)

    class FallbackBackend(BaseBackend):
        def __init__(self, **options):
            super().__init__(**options)

            # Initialize both backends
            self.primary = TwilioBackend(**options.get('primary', {}))
            self.fallback = NexmoBackend(**options.get('fallback', {}))

        def send_sms(self, number, message):
            try:
                logger.info(f"Attempting to send SMS via primary provider")
                self.primary.send_sms(number, message)
                logger.info(f"SMS sent successfully via primary provider")
            except Exception as e:
                logger.warning(f"Primary provider failed: {e}")
                logger.info(f"Attempting fallback provider")
                try:
                    self.fallback.send_sms(number, message)
                    logger.info(f"SMS sent successfully via fallback provider")
                except Exception as e2:
                    logger.error(f"Fallback provider also failed: {e2}")
                    raise Exception("All SMS providers failed") from e2

        def send_bulk_sms(self, numbers, message):
            # Similar logic for bulk SMS
            failed_numbers = []

            for number in numbers:
                try:
                    self.send_sms(number, message)
                except Exception as e:
                    failed_numbers.append(number)
                    logger.error(f"Failed to send to {number}: {e}")

            if failed_numbers:
                raise Exception(f"Failed to send to {len(failed_numbers)} numbers")

.. code-block:: python

    # settings.py
    PHONE_VERIFICATION = {
        "BACKEND": "myapp.backends.FallbackBackend",
        "OPTIONS": {
            "primary": {
                "SID": os.getenv("TWILIO_SID"),
                "SECRET": os.getenv("TWILIO_SECRET"),
                "FROM": os.getenv("TWILIO_FROM"),
            },
            "fallback": {
                "KEY": os.getenv("NEXMO_KEY"),
                "SECRET": os.getenv("NEXMO_SECRET"),
                "FROM": os.getenv("NEXMO_FROM"),
            },
        },
        ...
    }

Internationalization (i18n) Support
------------------------------------

Send verification messages in different languages based on user preferences.

Overview
^^^^^^^^

The library automatically detects the user's language from the ``Accept-Language`` HTTP header
and localizes the verification message accordingly. This is useful for applications serving
users in multiple countries or regions.

Setup
^^^^^

First, ensure Django's internationalization is enabled in your ``settings.py``:

.. code-block:: python

    # settings.py
    USE_I18N = True
    LANGUAGE_CODE = 'en-us'

    LANGUAGES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('zh-hant', 'Traditional Chinese'),
        # Add more languages as needed
    ]

    LOCALE_PATHS = [
        BASE_DIR / 'locale',
    ]

Create Translation Files
^^^^^^^^^^^^^^^^^^^^^^^^^

Create translation files for your verification message. The message template in ``PHONE_VERIFICATION['MESSAGE']``
will be automatically translated:

.. code-block:: bash

    # Create locale directories
    mkdir -p locale/es/LC_MESSAGES
    mkdir -p locale/fr/LC_MESSAGES
    mkdir -p locale/zh_Hant/LC_MESSAGES

    # Generate message files
    django-admin makemessages -l es
    django-admin makemessages -l fr
    django-admin makemessages -l zh_Hant

Edit the generated ``.po`` files to add translations:

.. code-block:: po

    # locale/es/LC_MESSAGES/django.po
    msgid "Welcome to {app}! Please use security code {security_code} to proceed."
    msgstr "¡Bienvenido a {app}! Por favor usa el código de seguridad {security_code} para continuar."

    # locale/fr/LC_MESSAGES/django.po
    msgid "Welcome to {app}! Please use security code {security_code} to proceed."
    msgstr "Bienvenue sur {app}! Veuillez utiliser le code de sécurité {security_code} pour continuer."

    # locale/zh_Hant/LC_MESSAGES/django.po
    msgid "Welcome to {app}! Please use security code {security_code} to proceed."
    msgstr "歡迎使用 {app}! 請使用安全碼 {security_code} 繼續。"

Compile the translations:

.. code-block:: bash

    django-admin compilemessages

Usage
^^^^^

The library automatically reads the ``Accept-Language`` header from HTTP requests and sends
the verification message in the user's preferred language:

.. code-block:: javascript

    // Frontend: Set Accept-Language header
    fetch('/api/phone/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept-Language': 'es'  // Spanish
        },
        body: JSON.stringify({
            phone_number: '+1234567890'
        })
    });

The SMS sent to the user will automatically be in Spanish if you've provided a translation.

Programmatic Usage
^^^^^^^^^^^^^^^^^^

You can also specify the language programmatically when using the service directly:

.. code-block:: python

    from phone_verify.services import send_security_code_and_generate_session_token

    # Send verification in French
    session_token = send_security_code_and_generate_session_token(
        phone_number="+1234567890",
        language="fr"
    )

    # Or using the service class directly
    from phone_verify.services import PhoneVerificationService

    service = PhoneVerificationService(
        phone_number="+1234567890",
        language="zh-hant"  # Traditional Chinese
    )

    backend = service.backend
    security_code, session_token = backend.create_security_code_and_session_token(
        phone_number="+1234567890"
    )

    service.send_verification("+1234567890", security_code)

Language Code Format
^^^^^^^^^^^^^^^^^^^^

The library accepts standard language codes:

- Simple codes: ``en``, ``es``, ``fr``, ``de``, ``ja``, ``zh``
- Locale-specific: ``en-US``, ``en-GB``, ``zh-Hans`` (Simplified Chinese), ``zh-Hant`` (Traditional Chinese)
- The first language in comma-separated ``Accept-Language`` headers is used
- Quality values (``q=``) are ignored; only the first language is considered

Fallback Behavior
^^^^^^^^^^^^^^^^^

If a translation is not available for the requested language, the library falls back to
the default message defined in ``PHONE_VERIFICATION['MESSAGE']``.

Phone Number Update Flow
-------------------------

Allow users to change their phone number with verification.

Implementation
^^^^^^^^^^^^^^

.. code-block:: python

    # myapp/views.py
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from rest_framework.permissions import IsAuthenticated
    from phone_verify.api import VerificationViewSet
    from phone_verify.services import send_security_code_and_generate_session_token

    class PhoneUpdateViewSet(VerificationViewSet):
        permission_classes = [IsAuthenticated]

        @action(detail=False, methods=['POST'])
        def request_change(self, request):
            """Step 1: Request phone number change"""
            new_phone = request.data.get('new_phone_number')

            # Validate new phone is not already in use
            from django.contrib.auth import get_user_model
            User = get_user_model()

            if User.objects.filter(phone_number=new_phone).exists():
                return Response(
                    {"error": "Phone number already in use"},
                    status=400
                )

            # Send verification to new number
            session_token = send_security_code_and_generate_session_token(new_phone)

            # Store in session
            request.session['pending_phone_change'] = {
                'user_id': request.user.id,
                'new_phone': new_phone
            }

            return Response({
                "message": "Verification code sent to new number",
                "session_token": session_token
            })

        @action(detail=False, methods=['POST'])
        def confirm_change(self, request):
            """Step 2: Verify code and update phone"""
            from phone_verify.serializers import SMSVerificationSerializer

            # Verify code
            serializer = SMSVerificationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Get pending change
            pending = request.session.get('pending_phone_change')
            if not pending or pending['user_id'] != request.user.id:
                return Response({"error": "Invalid session"}, status=400)

            # Update user's phone
            request.user.phone_number = pending['new_phone']
            request.user.save()

            del request.session['pending_phone_change']

            return Response({
                "message": "Phone number updated successfully",
                "new_phone": request.user.phone_number
            })

See Also
--------

- :doc:`integration` - Basic integration examples
- :doc:`api_reference` - Complete API documentation
- :doc:`security` - Security best practices
- :doc:`customization` - Creating custom backends
