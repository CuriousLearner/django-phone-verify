import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-phone-verify",
    version="3.0.0",
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
        "PyJWT>=2.6.0",
        "python-dotenv>=0.21.1",
        "phonenumbers>=8.10.2",
        "django-phonenumber-field>=2.1.0",
    ],
    extras_require={
        "twilio": ["twilio"],
        "nexmo": ["nexmo"],
        "all": ["twilio", "nexmo"],
    },
    project_urls={
        "Documentation": "https://www.sanyamkhurana.com/django-phone-verify/",
        "Changelog": "https://www.sanyamkhurana.com/django-phone-verify/CHANGELOG",
        "Code": "https://github.com/CuriousLearner/django-phone-verify",
        "Tracker": "https://github.com/CuriousLearner/django-phone-verify/issues",
        "Funding": "#TBD"
    },
    classifiers=[
        "Environment :: Web Environment",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
