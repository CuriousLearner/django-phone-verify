#!/usr/bin/env python
import os
import sys
import pytest

import django
from django.conf import settings
from django.test.utils import get_runner


if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'phone_verify.tests.test_settings'
    django.setup()
    result = pytest.main(['phone_verify'])
    sys.exit(bool(result))
