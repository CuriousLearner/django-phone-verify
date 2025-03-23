.. _integration:

Integration Guide
=================

This guide explains how to integrate ``django-phone-verify`` into your user signup process.
It includes two approaches:

1. Using Django REST Framework (DRF)
2. Using standard Django views and forms (non-DRF)


Approach 1: Integration with Django REST Framework (DRF)
--------------------------------------------------------

This method is ideal if your project uses APIs for registration.

1. **Create a custom ViewSet**

.. code-block:: python

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
            phone_serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
            phone_serializer.is_valid(raise_exception=True)

            user_serializer = serializers.YourUserSerializer(data=request.data)
            user_serializer.is_valid(raise_exception=True)

            user = services.create_user_account(**user_serializer.validated_data)

            return Response(user_serializer.data)

2. **Create serializers**

.. code-block:: python

    from rest_framework import serializers
    from phone_verify.serializers import SMSVerificationSerializer

    class YourUserSerializer(serializers.Serializer):
        username = serializers.CharField()
        email = serializers.EmailField()
        password = serializers.CharField()

    class YourCustomSerializer(YourUserSerializer, SMSVerificationSerializer):
        pass

3. **Create service for user creation**

.. code-block:: python

    from django.contrib.auth import get_user_model

    def create_user_account(username, email, password, **extra):
        return get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra,
        )

4. **Register viewset in urls.py**

.. code-block:: python

    from rest_framework.routers import DefaultRouter
    from yourapp.api import YourCustomViewSet

    router = DefaultRouter(trailing_slash=False)
    router.register('phone', YourCustomViewSet, basename='phone')
    urlpatterns = router.urls


Approach 2: Integration Without DRF (Using Django Views & Forms)
----------------------------------------------------------------

If you're using Django templates and standard views, you can integrate phone verification manually using the core service API.

This process happens in **two steps**:

1. First, the user submits their phone number to request a verification code.
2. Then, on a second form, they enter the code they received to verify their number and proceed with registration.

1. **Forms**

.. code-block:: python

    from django import forms

    class PhoneRequestForm(forms.Form):
        phone_number = forms.CharField()

    class VerificationForm(forms.Form):
        phone_number = forms.CharField(widget=forms.HiddenInput)
        security_code = forms.CharField()
        username = forms.CharField()
        email = forms.EmailField()
        password = forms.CharField(widget=forms.PasswordInput)

2. **Views**

.. code-block:: python

    from django.shortcuts import render, redirect
    from phone_verify.services import PhoneVerificationService
    from django.contrib.auth import get_user_model
    from .forms import PhoneRequestForm, VerificationForm

    def request_code_view(request):
        if request.method == 'POST':
            form = PhoneRequestForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data['phone_number']
                verifier = PhoneVerificationService(phone)
                verifier.send_verification()
                return redirect(f'/verify/?phone_number={phone}')
        else:
            form = PhoneRequestForm()
        return render(request, 'request_code.html', {'form': form})

    def verify_and_register_view(request):
        if request.method == 'POST':
            form = VerificationForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data['phone_number']
                code = form.cleaned_data['security_code']
                verifier = PhoneVerificationService(phone)
                if verifier.verify(code):
                    get_user_model().objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                    )
                    return redirect('login')
        else:
            phone = request.GET.get('phone_number', '')
            form = VerificationForm(initial={'phone_number': phone})
        return render(request, 'verify_and_register.html', {'form': form})

3. **Templates**

**request_code.html**

.. code-block:: html
    :force:

    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Send Verification Code</button>
    </form>

**verify_and_register.html**

.. code-block:: html
    :force:

    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Verify & Register</button>
    </form>

----

Choose the approach that best fits your architecture. For APIs, use DRF. For standard form submissions, follow the manual integration path.

For sandbox or custom backend support, see the :doc:`customization` guide.
