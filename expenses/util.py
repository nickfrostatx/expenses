# -*- coding: utf-8 -*-
"""Utility functions."""

from base64 import urlsafe_b64encode
from datetime import date
from flask import request, session, abort, redirect, url_for
from functools import wraps
import operator
import os


class LazyObject(object):

    """Lazily call a factory to create an object."""

    def __init__(self, init):
        self._init = init
        self._wrapped = None

    @property
    def instantiated(self):
        return self._wrapped is not None

    def __setattr__(self, name, value):
        # Avoid infinite recursion when using called_func
        if name in ('_init', '_wrapped'):
            object.__setattr__(self, name, value)
        else:
            if not self.instantiated:
                self._wrapped = self._init()
            setattr(self._wrapped, name, value)

    def called_func(func):
        def called(self, *args, **kwargs):
            if not self.instantiated:
                self._wrapped = self._init()
            return func(self._wrapped, *args, **kwargs)
        return called

    __getattr__ = called_func(getattr)
    __delattr__ = called_func(delattr)

    # List, tuple, dictionary method support
    __getitem__ = called_func(operator.getitem)
    __setitem__ = called_func(operator.setitem)
    __delitem__ = called_func(operator.delitem)
    __iter__ = called_func(iter)
    __len__ = called_func(len)
    __contains__ = called_func(operator.contains)
    del called_func

    def __repr__(self):
        if self.instantiated:
            return repr(self._wrapped)
        return '<LazyObject wrapping {0}>'.format(repr(self._init))


def check_csrf(fn):
    @wraps(fn)
    def inner(*a, **kw):
        token = request.form.get('token') or request.args.get('token')
        if not token or token != session['csrf']:
            abort(403)
        return fn(*a, **kw)
    return inner


def require_noauth(fn):
    @wraps(fn)
    def inner(*a, **kw):
        if session.authed:
            return redirect('/', code=303)
        return fn(*a, **kw)
    return inner


def require_auth(fn):
    @wraps(fn)
    def inner(*a, **kw):
        if not session.authed:
            return redirect(url_for('.login_page'), code=303)
        return fn(*a, **kw)
    return inner


def date_format(d, today=None):
    if today is None:
        today = date.today()
    if d == today:
        return 'Today'
    elif (today - d).days == -1:
        return 'Tomorrow'
    elif (today - d).days == 1:
        return 'Yesterday'

    month = d.year * 12 + d.month
    this_month = today.year * 12 + today.month
    if month == this_month:
        return 'This month'
    elif abs(month - this_month) <= 3:
        return '{0:%B}'.format(d)
    else:
        return '{0:%B %Y}'.format(d)


def price_filter(amount):
    return u'${0:,.2f}'.format(amount / 100.0)


def random_string(size):
    """Generate a random base64 string from urandom."""
    if size < 0:
        raise ValueError('Negative lengths are not allowed')
    elif size % 4 != 0:
        raise ValueError('The length must be a multiple of 4')
    n_bytes = size * 3 // 4
    return urlsafe_b64encode(os.urandom(n_bytes)).decode()
