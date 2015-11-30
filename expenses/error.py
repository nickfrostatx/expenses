# -*- coding: utf-8 -*-
"""Catch-all error handling."""

from flask import Flask, render_template
from functools import wraps
import werkzeug.exceptions


def register_error_handler(app, fn):
    """Register a catch-all handler to an app or blueprint."""
    for status in werkzeug.exceptions.default_exceptions:
        if status != 500:
            app.errorhandler(status)(fn)

    # If it's not a Blueprint
    if isinstance(app, Flask):
        @wraps(fn)
        def handle_500(e):
            if not isinstance(e, werkzeug.exceptions.HTTPException):
                e = werkzeug.exceptions.InternalServerError()
            return fn(e)
        app.errorhandler(500)(handle_500)

    return fn


def errorhandler(app):
    """Return a decorator that registers fn as an error handler."""
    def decorator(fn):
        register_error_handler(app, fn)
        return fn
    return decorator


def html_handler(e):
    """Render the HTML error page for a given HTTPException."""
    return render_template('views/error.html', e=e), e.code
