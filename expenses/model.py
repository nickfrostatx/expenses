# -*- coding: utf-8 -*-
"""Database models."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(254))
    username = db.Column(db.String(254), unique=True)
    password = db.Column(db.String(60))
    purchases = db.relationship('Purchase', backref='user')


class Purchase(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(254))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cost = db.Column(db.Integer)
    date = db.Column(db.Date)
