# -*- coding: utf-8 -*-
"""Main HTML views."""

from bcrypt import gensalt, hashpw
from flask import Blueprint, request, session, flash, url_for, redirect, \
                  render_template
from sqlalchemy.exc import IntegrityError
from werkzeug.security import safe_str_cmp
from .model import db, User
from .util import check_csrf


views = Blueprint('views', __name__, template_folder='templates')


@views.route('/')
def home():
    return render_template('views/home.html')


@views.route('/login/')
def login_page():
    return render_template('views/login.html')


@views.route('/signup/')
def signup_page():
    return render_template('views/signup.html')


@views.route('/auth', methods=['POST'])
@check_csrf
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        pw_hash = hashpw(password.encode(), user.password.encode()).decode()
        if safe_str_cmp(pw_hash, user.password):
            session.rotate()
            session['user'] = user.id
            return redirect('/', code=303)
        else:
            flash('Incorrect password', 'error')
    else:
        flash('No such user', 'error')
    return redirect(url_for('.login_page', username=username), code=303)


@views.route('/users', methods=['POST'])
@check_csrf
def signup():
    valid = True
    for field in ('name', 'username', 'password'):
        if not request.form.get(field, ''):
            flash(field.capitalize() + ' is required', 'error')
            valid = False
    if valid:
        name = request.form.get('user')
        username = request.form.get('username')
        password = request.form.get('password')
        pw_hash = hashpw(password.encode(), gensalt()).decode()
        user = User(name=name, username=username, password=pw_hash)
        db.session.add(user)
        try:
            db.session.commit()
            session['user'] = user.id
            return redirect('/', code=303)
        except IntegrityError:
            flash('That username already exists')
    return redirect(url_for('.signup_page'), code=303)


@views.route('/logout')
@check_csrf
def logout():
    session.clear()
    return redirect('/')
