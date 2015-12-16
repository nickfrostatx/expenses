# -*- coding: utf-8 -*-
"""Main HTML views."""

from bcrypt import gensalt, hashpw
from datetime import datetime, date
from flask import Blueprint, request, session, flash, url_for, redirect, \
                  jsonify, render_template
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from werkzeug.security import safe_str_cmp
from .model import db, User, Purchase
from .util import check_csrf, require_auth, require_noauth, date_filter, \
                  price_filter


views = Blueprint('views', __name__, template_folder='templates')

PER_PAGE = 50


def purchases_obj(page):
    total_purchases = db.session.query(Purchase).count()
    purchases = db.session.query(Purchase).order_by(Purchase.date.desc()) \
        .slice(page * PER_PAGE, (page + 1) * PER_PAGE)
    data = {
        'expenses': [{
            'user': p.user.name,
            'name': p.name,
            'price': price_filter(p.cost),
            'date': date_filter(p.date),
        } for p in purchases],
        'links': {},
    }
    if total_purchases > (page + 1) * PER_PAGE:
        data['links']['next'] = url_for('.get_expenses', page=page + 1,
                                        _external=True)
    return data


@views.route('/')
def home():
    query = db.session.query(User.name, func.sum(Purchase.cost) \
        .label('total')).outerjoin(Purchase).group_by(User)
    users = [(r.name, int(r.total or 0)) for r in query]
    if users:
        avg = float(sum(user[1] for user in users)) / len(users)
    else:
        avg = 0
    purchases = purchases_obj(0)
    return render_template('views/home.html', users=users, avg=avg,
                           purchases=purchases, today=date.today())


@views.route('/expenses', methods=['GET'])
def get_expenses():
    try:
        page = int(request.args.get('page', '0'))
    except ValueError:
        return jsonify({'msg': 'Invalid page number.'}), 404
    if page < 0:
        return jsonify({'msg': 'Invalid page number.'}), 404
    data = purchases_obj(page)
    if not data['expenses']:
        return jsonify({'msg': 'Invalid page number.'}), 404
    return jsonify(data)


@views.route('/expenses', methods=['POST'])
@require_auth
@check_csrf
def add_expense():
    valid = True
    name = request.form.get('name')
    if not name:
        flash('A name is required', 'error')
        valid = False
    try:
        price = int(float(request.form.get('price')) * 100)
        if price <= 0:
            flash('The price must be greater than $0.00', 'error')
            valid = False
    except (TypeError, ValueError):
        flash('Expected a valid price', 'error')
        valid = False
    try:
        p_date = datetime.strptime(request.form.get('date'), '%m/%d/%Y').date()
    except (TypeError, ValueError):
        flash('Expected a valid date', 'error')
        valid = False
    if valid:
        purchase = Purchase(name=name, cost=price, date=p_date,
                            user_id=session['user'])
        db.session.add(purchase)
        db.session.commit()
        return redirect(url_for('.home'), code=303)
    else:
        return redirect(url_for('.home'), code=303)


@views.route('/login/')
@require_noauth
def login_page():
    return render_template('views/login.html')


@views.route('/signup/')
@require_noauth
def signup_page():
    return render_template('views/signup.html')


@views.route('/auth', methods=['POST'])
@require_noauth
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
            return redirect(url_for('.home'), code=303)
        else:
            flash('Incorrect password', 'error')
            return redirect(url_for('.login_page', username=username), code=303)
    else:
        flash('No such user', 'error')
        return redirect(url_for('.login_page'), code=303)



@views.route('/users', methods=['POST'])
@require_noauth
@check_csrf
def signup():
    valid = True
    for field in ('name', 'username', 'password'):
        if not request.form.get(field, ''):
            flash(field.capitalize() + ' is required', 'error')
            valid = False
    if valid:
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        pw_hash = hashpw(password.encode(), gensalt()).decode()
        user = User(name=name, username=username, password=pw_hash)
        db.session.add(user)
        try:
            db.session.commit()
            session['user'] = user.id
            return redirect(url_for('.home'), code=303)
        except IntegrityError:
            flash('That username already exists', 'error')
    return redirect(url_for('.signup_page'), code=303)


@views.route('/logout')
@require_auth
@check_csrf
def logout():
    session.clear()
    return redirect(url_for('.home'))
