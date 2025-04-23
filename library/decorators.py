"""
This module contains custom decorators for the library management system.
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def login_required_custom(view_func):
    """
    Custom decorator to ensure a user is authenticated before accessing a view.
    This decorator checks if the user is authenticated using the session variable
    and redirects to the login page if not authenticated.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        """
        Inner function that performs the authentication check.
        """
        if not request.session.get('is_authenticated', False):
            messages.error(request, 'You need to log in to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view