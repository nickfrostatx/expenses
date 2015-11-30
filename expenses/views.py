# -*- coding: utf-8 -*-
"""Main HTML views."""

from flask import Blueprint, render_template


views = Blueprint('views', __name__, template_folder='templates')


@views.route('/')
def home():
    return render_template('views/home.html')
