from functools import wraps
from flask import request, abort


def _get_identifier(id_sha1, id_sha2):
    """ Function to generate the identifier of a patch based on two shas given
        The reason we keep this function is that in the future we might change
        the '-' to something more sophisticated.
    """
    return '-'.join([id_sha1, id_sha2])


def allow_from(ip):
    """Restrict access by IP address"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.remote_addr != ip:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
