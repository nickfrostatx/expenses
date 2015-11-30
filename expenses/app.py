# -*- coding: utf-8 -*-
"""Flask application factory."""

from flask import Flask
from redis import StrictRedis
from . import __name__ as package_name
import os


def create_app():
    """Return an instance of the main Flask application."""
    app = Flask(package_name)

    # TODO: do some config
    app.redis = StrictRedis()

    from .error import register_error_handler, html_handler
    register_error_handler(app, html_handler)

    from .session import RedisSessionInterface
    app.session_interface = RedisSessionInterface()

    from .views import views
    app.register_blueprint(views)

    return app
