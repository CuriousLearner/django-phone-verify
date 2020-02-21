How to Use Django Phone Verify?
=====================================


Installation
------------

.. code-block:: shell

    pip install django-phone-verify


Configuration
-------------

- Add app to ``INSTALLED_APPS``:

.. code-block:: python

    # In settings.py:

    INSTALLED_APPS = [
        ...
        'phone_verify',
    ]

- Add settings in your ``settings.py`` file:

.. code-block:: python

    # Settings for phone_verify
    PHONE_VERIFICATION = {
        'BACKEND': 'phone_verify.backends.twilio.TwilioBackend',
        'OPTIONS': {
            'SID': 'fake',
            'SECRET': 'fake',
            'FROM': '+14755292729',
            'SANDBOX_TOKEN':'123456',
        },
        'TOKEN_LENGTH': 6,
        'MESSAGE': 'Welcome to {app}! Please use security code {security_code} to proceed.',
        'APP_NAME': 'Phone Verify',
        'SECURITY_CODE_EXPIRATION_TIME': 3600,  # In seconds only
        'VERIFY_SECURITY_CODE_ONLY_ONCE': False,  # If False, then a security code can be used multiple times for verification
    }


- Migrate the database:

.. code-block:: shell

    python manage.py migrate

This would create ``SMSVerification`` table, which is used to store ``phone_number``, ``session_token`` and ``security_code``.

Usage
-----

**NOTE**: ``django-phone-verify`` provides few APIs which can be added to your list of API endpoints. Its functionality can be extended further based on your use-case as explained below.

Case 1: Verify phone number before/after user registration
**********************************************************

This case is suitable if you simply want to access the endpoints to register and verify a phone number (before or after the user registration).

To access the endpoints available in `api_endpoints.rst`_, you just need to update your API's URLs.

.. _api_endpoints.rst: ../phone_verify/docs/api_endpoints.rst

- Add a default router:

.. code-block:: python

    # In urls.py

    from rest_framework.routers import DefaultRouter
    from phone_verify.api import VerificationViewSet

    default_router = DefaultRouter(trailing_slash=False)
    default_router.register('phone', VerificationViewSet, basename='phone')

    urlpatterns = default_router.urls

**NOTE**: It is recommended that you should verify the phone number of users before their registration.

Case 2: Verify phone number at the time of user registration
************************************************************

This is the case when you choose to integrate your user registration process with phone number verification.

**NOTE**: Here, you'll first register a phone number using ``/api/phone/register`` and then, will use the endpoint ``/api/phone/verify_and_register`` to create a user on successful verification of the phone number.

- Add a default router in *urls* to redirect on one of your custom viewset:

.. code-block:: python

    # In urls.py

    from rest_framework.routers import DefaultRouter
    from yourapp.api import YourCustomViewSet

    default_router = DefaultRouter(trailing_slash=False)

    default_router.register('phone', YourCustomViewSet, basename='phone')

    urlpatterns = default_router.urls


- Create *YourCustomSerializer*:

.. code-block:: python

    # In serializers.py

    from rest_framework import serializers

    from phone_verify.serializers import SMSVerificationSerializer

    class YourUserSerializer(serializers.Serializer):
        username = serializers.CharField(required=True)
        email = serializers.EmailField(required=True)
        password = serializers.CharField(required=True)
        first_name = serializers.CharField(default="First")
        ...


    class YourCustomSerializer(UserSerializer, SMSVerificationSerializer):
        ...


- Add a service to create users:

.. code-block:: python

    # In your services.py

    from django.contrib.auth import get_user_model

    def create_user_account(username, email, password, **extra_args):
        user = get_user_model().objects.create_user(
            username=username, email=email, password=password, **extra_args
        )
        ...
        return user


- Create *YourCustomViewSet*:

.. code-block:: python

    # In your api.py

    from rest_framework.decorators import action
    from rest_framework.permissions import AllowAny
    from rest_framework.response import Response

    from phone_verify.api import VerificationViewSet
    from phone_verify import serializers as phone_serializers

    from . import services, serializers


    class YourCustomViewSet(VerificationViewSet):

        @action(detail=False, methods=['POST'], permission_classes=[AllowAny], serializer_class=serializers.YourCustomSerializer)
        def verify_and_register(self, request):
            """Function to verify phone number and register a user

            Most of the code here is corresponding to the "verify" view already present in the package.

            """

            serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Add your custom code here.
            # An example is shown below:

            serializer = serializers.YourUserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = services.create_user_account(**serializer.validated_data)

            return Response(serializer.data)

**NOTE**:

1. Using the above method, we are coupling the phone verification and user registration process. One can also override the ``verify`` view to perform additional actions such as registering the user, registering a company with the verified phone number, etc.

2. After inheriting ``VerificationViewSet``, in case you would like to override ``get_serializer_class``, then after specifying all your conditions, you must return ``self.serializer_class``. For example:

.. code-block:: python

    def get_serializer_class(self):
        if self.action == 'verify_and_register':
            return serializers.YourCustomSerializer
        ...
        else:
            return self.serializer_class

Otherwise, serializer classes for ``verify`` and ``register`` views will not be available.

3. Latest ``security_code`` generated for a ``phone_number`` can be found at ``/admin/phone_verify/smsverification/`` URL.

4. Django's ``post_save`` signal can be leveraged through its usage in ``phone_verify.models.SMSVerification`` function. Additional functionality can be hooked via the ``post_save`` signal by creating the following receiver.

.. code-block:: python

    # In signals.py
    from phone_verify.models import SMSVerification
    from django.db.models.signals import post_save
    from django.dispatch import receiver
    from django.core.mail import send_mail


    # `send_phone_verify_email` function will get fired when a new entry is created or the model instance is updated
    @receiver(post_save, sender=SMSVerification)
    def send_phone_verify_email(sender, instance=None, created=None, **kwargs):
        # Check if the instance is created or not
        if created:
            send_mail(
                subject='Subject here',
                message='Here is the message.',
                from_email='from@example.com',
                recipient_list=['to@example.com'],
                fail_silently=False,
            )
