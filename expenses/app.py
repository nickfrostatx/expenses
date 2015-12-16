# -*- coding: utf-8 -*-
"""Flask application factory."""

from flask import Flask
from redis import from_url
from . import __name__ as package_name
import os


def create_app():
    """Return an instance of the main Flask application."""
    app = Flask(package_name)

    app.config.setdefault('REDIS_URL', 'redis://localhost')

    from .model import db
    db.init_app(app)

    @app.before_first_request
    def init_db():
        app.redis = from_url(app.config['REDIS_URL'])

    from .error import register_error_handler, html_handler
    register_error_handler(app, html_handler)

    from .session import LazyRedisSessionInterface
    app.session_interface = LazyRedisSessionInterface()

    from .util import price_filter
    app.jinja_env.filters['price'] = price_filter

    from .views import views
    app.register_blueprint(views)

    return app
