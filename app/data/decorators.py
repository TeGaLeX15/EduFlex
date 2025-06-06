from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator
