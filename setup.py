import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-phone-verify",
    version="2.0.1",
    packages=find_packages(),
    include_package_data=True,
    license="GPLv3",
    description="A Django app to support phone number verification using security code sent via SMS.",
    long_description=README,
    url="https://github.com/CuriousLearner/django-phone-verify",
    author="Sanyam Khurana",
    author_email="sanyam@sanyamkhurana.com",
    install_requires=[
        "django>=2.1.5",
        "djangorestframework>=3.9.0",
        "PyJWT>=1.7.1",
        "python-dotenv>=0.10.0",
        "phonenumbers>=8.10.2",
        "django-phonenumber-field>=2.1.0",
        "twilio>=6.21.0",
        "nexmo>=2.4.0",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
