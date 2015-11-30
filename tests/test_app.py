# -*- coding: utf-8 -*-
"""Test app factory."""

from expenses.app import create_app
from flask import Flask


def test_create_app():
    app = create_app()
    assert isinstance(app, Flask)
