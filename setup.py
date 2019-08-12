import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-phone-verify",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    license="GPLv3",
    description="A Django app to support phone number verification using OTP sent via SMS.",
    long_description=README,
    url="https://github.com/CuriousLearner/django-phone-verify",
    author="Sanyam Khurana",
    author_email="sanyam@sanyamkhurana.com",
    install_requires=[
        "django>=2.1.5",
        "djangorestframework>=3.9.0",
        "python-dotenv>=0.10.0",
        "phonenumbers>=8.10.2",
        "django-phonenumber-field>=2.1.0",
        "twilio>=6.21.0",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 2.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
