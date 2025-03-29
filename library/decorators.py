from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def login_required_custom(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_authenticated', False):
            messages.error(request, 'You need to log in to access this page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view