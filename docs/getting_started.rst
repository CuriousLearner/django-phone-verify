Getting Started
===============

Installation
------------

You can install ``django-phone-verify`` using ``pip``. The package supports optional extras
for different SMS backends.

.. code-block:: shell

    # Core installation (requires configuring your own backend)
    pip install django-phone-verify

    # Twilio support
    pip install django-phone-verify[twilio]

    # Nexmo (Vonage) support
    pip install django-phone-verify[nexmo]

    # All optional dependencies (recommended for exploring)
    pip install django-phone-verify[all]

Configuration
-------------

1. **Add the app to your ``INSTALLED_APPS``**

.. code-block:: python

    # settings.py

    INSTALLED_APPS = [
        ...
        'phone_verify',
        ...
    ]

2. **Add configuration to ``settings.py``**

.. code-block:: python

    PHONE_VERIFICATION = {
        'BACKEND': 'phone_verify.backends.twilio.TwilioBackend',  # Or NexmoBackend
        'OPTIONS': {
            'SID': 'fake',
            'SECRET': 'fake',
            'FROM': '+14755292729',
            'SANDBOX_TOKEN': '123456',
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600,  # In seconds
        'VERIFY_SECURITY_CODE_ONLY_ONCE': False,
    }

3. **Run migrations**

.. code-block:: shell

    python manage.py migrate

This creates the ``SMSVerification`` table, which stores the phone number, session token, and security code.

Usage
-----

.. note::

   ``django-phone-verify`` provides ready-to-use APIs for phone number verification, which can be extended for custom workflows.

Case 1: Verify phone number before or after user registration
**************************************************************

This setup allows you to verify a phone number independently, either before or after user registration.

Add the default router and register the built-in viewset:

.. code-block:: python

    # urls.py

    from rest_framework.routers import DefaultRouter
    from phone_verify.api import VerificationViewSet

    router = DefaultRouter(trailing_slash=False)
    router.register('phone', VerificationViewSet, basename='phone')

    urlpatterns = router.urls

.. note::

   It is recommended to verify the user’s phone number **before** registration.

Case 2: Verify phone number during user registration
****************************************************

This use case integrates phone number verification with your user registration flow.
You will use the built-in phone verification mechanism and register a user only after the phone is verified.

1. **Define your custom ViewSet**

Start by extending the base ``VerificationViewSet`` and adding a custom action to verify the phone and register a user:

.. code-block:: python

    # api.py

    from rest_framework.decorators import action
    from rest_framework.permissions import AllowAny
    from rest_framework.response import Response
    from phone_verify.api import VerificationViewSet
    from phone_verify import serializers as phone_serializers

    from . import services, serializers

    class YourCustomViewSet(VerificationViewSet):

        @action(
            detail=False,
            methods=['POST'],
            permission_classes=[AllowAny],
            serializer_class=serializers.YourCustomSerializer,
        )
        def verify_and_register(self, request):
            """
            Verify phone number and register a user
            """
            phone_serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
            phone_serializer.is_valid(raise_exception=True)

            user_serializer = serializers.YourUserSerializer(data=request.data)
            user_serializer.is_valid(raise_exception=True)

            user = services.create_user_account(**user_serializer.validated_data)

            return Response(user_serializer.data)

.. note::

   If you override ``get_serializer_class``, be sure to return ``self.serializer_class`` as fallback:

   .. code-block:: python

       def get_serializer_class(self):
           if self.action == 'verify_and_register':
               return serializers.YourCustomSerializer
           return self.serializer_class

2. **Create your serializers**

.. code-block:: python

    # serializers.py

    from rest_framework import serializers
    from phone_verify.serializers import SMSVerificationSerializer

    class YourUserSerializer(serializers.Serializer):
        username = serializers.CharField(required=True)
        email = serializers.EmailField(required=True)
        password = serializers.CharField(required=True)
        first_name = serializers.CharField(default="First")
        ...

    class YourCustomSerializer(YourUserSerializer, SMSVerificationSerializer):
        pass

3. **Define a user creation service**

.. code-block:: python

    # services.py

    from django.contrib.auth import get_user_model

    def create_user_account(username, email, password, **extra_args):
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_args
        )
        return user

4. **Register your custom viewset in ``urls.py``**

Now expose your custom view via URL routing:

.. code-block:: python

    # urls.py

    from rest_framework.routers import DefaultRouter
    from yourapp.api import YourCustomViewSet

    router = DefaultRouter(trailing_slash=False)
    router.register('phone', YourCustomViewSet, basename='phone')

    urlpatterns = router.urls

----

Additional Notes
----------------

1. The latest security code for a phone number can be found at:

   .. code-block:: none

       /admin/phone_verify/smsverification/

2. You can hook into phone verification using Django signals. For example:

   .. code-block:: python

       # signals.py

       from django.core.mail import send_mail
       from django.db.models.signals import post_save
       from django.dispatch import receiver
       from phone_verify.models import SMSVerification

       @receiver(post_save, sender=SMSVerification)
       def send_phone_verify_email(sender, instance=None, created=None, **kwargs):
           if created:
               send_mail(
                   subject='Phone verification created',
                   message='A new verification entry was added.',
                   from_email='no-reply@example.com',
                   recipient_list=['to@example.com'],
                   fail_silently=False,
               )

----

You’re all set! 🎉 Customize further by writing your own backends, sandbox services, or hooking into signals to match your product’s workflow.
