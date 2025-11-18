from functools import wraps
from flask import session, redirect, url_for, request, flash

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("auth_bp.login"))

        return func(*args, **kwargs)

    return wrapper


def validate_password_strength(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        special_characters = "!@#$%^&*()_+-=[]{};:,.<>/?"
        if request.method == "POST":
            password = request.form.get("password", "").strip()
            missing = []

            if len(password) < 8:
                missing.append("at least 8 characters")
            if not any(c.isupper() for c in password):
                missing.append("at least one uppercase letter")
            if not any(c.islower() for c in password):
                missing.append("at least one lowercase letter")
            if not any(c in special_characters for c in password):
                missing.append("at least one special character")

            if missing:
                flash(f"Weak password! use: {missing[0]}")
                return redirect(url_for("auth_bp.signup"))

        return func(*args, **kwargs)
    return wrapper
