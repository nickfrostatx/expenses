# -*- coding: utf-8 -*-
"""Test utility functions."""

from expenses.views import views
import flask
import pytest


@pytest.fixture
def client():
    app = flask.Flask(__name__)
    app.debug = True
    app.register_blueprint(views)
    return app.test_client()


def test_home(client):
    rv = client.get('/')
    assert b'<h1>It works!</h1>' in rv.data
    assert rv.status_code == 200
