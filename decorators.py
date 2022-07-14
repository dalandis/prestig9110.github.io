from functools import wraps
from flask_discord import DiscordOAuth2Session
from hello import app, oauth
from flask import request, jsonify

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = oauth.fetch_user()

        if not str(user.id) in app.config["PERMISSIONS"]:
            return 'Доступ запрещен'
        return f(*args, **kwargs)
    return decorated_function

def bearer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "Authorization" in request.headers:
            data = request.headers['Authorization']
            token = str.replace(str(data), 'Bearer ','')
            if token != app.config["BEARER_SUPERHUB"]:
                return jsonify({"error": "Authentication failed", "status_code": 401}), 401
        else:
            return jsonify({"error": "Authentication failed", "status_code": 401}), 401
        return f(*args, **kwargs)
    return decorated_function

def protect_route(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not oauth.authorized:
            return jsonify({"error": "Authentication not found", "status_code": 401}), 401
        return f(*args, **kwargs)
    return decorated_function