# -*- coding: utf-8 -*-
"""Database models."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(254))
    username = db.Column(db.String(254), unique=True)
    password = db.Column(db.String(60))
