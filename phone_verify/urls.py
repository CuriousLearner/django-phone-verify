# Third Party Stuff
from rest_framework.routers import DefaultRouter

# phone_verify
from .api import VerificationViewSet

default_router = DefaultRouter(trailing_slash=False)
default_router.register("phone", VerificationViewSet, basename="phone")

urlpatterns = list(default_router.urls)
