from functools import wraps
from flask import session, redirect, url_for, jsonify, request


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'access_token' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'unauthorized'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated
