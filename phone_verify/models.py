# Standard Library
import uuid

# Third Party Stuff
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _
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
    otp = models.CharField(_('OTP'), max_length=120)
    phone_number = PhoneNumberField(_('Phone Number'))
    session_code = models.CharField(_('Device Session Code'), max_length=500)

    class Meta:
        db_table = 'sms_verification'
        verbose_name = _('SMS Verification')
        verbose_name_plural = _('SMS Verifications')
        ordering = ('-modified_at', )
        unique_together = ('otp', 'phone_number', 'session_code')

    def __str__(self):
        return '{}: {}'.format(str(self.phone_number), self.otp)
