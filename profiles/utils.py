"""
Utility functions for retrieving and generating forms for the
site-specific user profile model specified in the
``AUTH_PROFILE_MODULE`` setting.

"""

from django import forms
from django.apps import apps
from django.conf import settings

# idea from https://bitbucket.org/psagers/django-auth-ldap/pull-requests/15/django-17-compatibility-for-using-custom/diff#chg-django_auth_ldap/backend.py
try:
    from django.contrib.auth.models import SiteProfileNotAvailable
except ImportError:
    SiteProfileNotAvailable = Exception


def get_profile_form(user):
    """
    Return a form class (a subclass of the default ``ModelForm``)
    suitable for creating/editing instances of the site-specific user
    profile model, as defined by the ``AUTH_PROFILE_MODULE``
    setting. If that setting is missing, raise
    ``django.contrib.auth.models.SiteProfileNotAvailable``.
    
    """
    class _ProfileForm(forms.ModelForm):
        class Meta:
            model = user.profile
            exclude = ('user',) # User will be filled in by the view.
    return _ProfileForm
