# Standard Library
import uuid

# Third Party Stuff
from django.db import models
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UUIDModel(models.Model):
    """ An abstract base class model that makes primary key `id` as UUID
    instead of default auto incremented number.
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class TimeStampedUUIDModel(UUIDModel):
    """An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields with UUID as primary_key field.
    """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class SMSVerification(TimeStampedUUIDModel):
    security_code = models.CharField(_("Security Code"), max_length=120)
    phone_number = PhoneNumberField(_("Phone Number"))
    session_token = models.CharField(_("Device Session Token"), max_length=500)
    is_verified = models.BooleanField(_("Security Code Verified"), default=False)

    class Meta:
        db_table = "sms_verification"
        verbose_name = _("SMS Verification")
        verbose_name_plural = _("SMS Verifications")
        ordering = ("-modified_at",)
        unique_together = ("security_code", "phone_number", "session_token")

    def __str__(self):
        return "{}: {}".format(str(self.phone_number), self.security_code)
