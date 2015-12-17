# -*- coding: utf-8 -*-
"""Test utility functions."""

from datetime import date
from expenses.util import LazyObject, check_csrf, date_format, random_string
import flask
import pytest


def test_lazy():
    class FooDict(dict):
        # Support setattr on a dict
        pass

    d = FooDict({'a': 1})

    def init_object():
        d['a'] += 1
        return d

    obj = LazyObject(init_object)

    assert not obj.instantiated
    assert '<LazyObject wrapping <function' in repr(obj)
    assert d['a'] == 1

    # Object is instantiated here
    assert obj['a'] == 2
    assert obj.instantiated
    assert repr(obj) == "{'a': 2}"
    assert len(obj) == 1

    obj.abc = 'def'
    assert hasattr(obj, 'abc')
    assert obj.abc == 'def'
    assert d.abc == 'def'

    del obj.abc
    assert not hasattr(obj, 'abc')
    assert not hasattr(d, 'abc')

    obj['b'] = 3
    assert obj['b'] == 3
    assert d['b'] == 3
    assert 'b' in obj

    assert set(iter(obj)) == set(['a', 'b'])

    del obj['b']
    assert 'b' not in obj

    # Make sure we only ran init_object once
    assert d['a'] == 2

    obj.clear()
    assert len(obj) == 0
    assert len(d) == 0


def test_check_csrf():
    app = flask.Flask(__name__)

    class FakeSessionInterface(flask.sessions.SessionInterface):

        def open_session(self, app, request):
            return {'csrf': 'somecsrf'}

        def save_session(self, app, session, response):
            pass

    app.session_interface = FakeSessionInterface()

    @app.route('/', methods=['POST'])
    @check_csrf
    def home():
        return 'abc'

    with app.test_client() as client:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        rv = client.post('/')
        assert rv.status_code == 403

        rv = client.post('/', headers=headers, data='token=')
        assert rv.status_code == 403

        rv = client.post('/', headers=headers, data='token=fake')
        assert rv.status_code == 403

        rv = client.post('/', headers=headers, data='token=somecsrf')
        assert rv.status_code == 200


def test_date_format():
    assert date_format(date(2015, 1, 1), date(2015, 1, 1)) == 'Today'

    assert date_format(date(2015, 1, 2), date(2015, 1, 1)) == 'Tomorrow'
    assert date_format(date(2015, 1, 1), date(2014, 12, 31)) == 'Tomorrow'

    assert date_format(date(2015, 1, 1), date(2015, 1, 2)) == 'Yesterday'
    assert date_format(date(2014, 12, 31), date(2015, 1, 1)) == 'Yesterday'

    assert date_format(date(2014, 12, 30), date(2015, 1, 1)) == 'December'
    assert date_format(date(2014, 11, 30), date(2014, 12, 31)) == 'November'
    assert date_format(date(2014, 9, 30), date(2014, 12, 31)) == 'September'
    assert date_format(date(2014, 8, 31), date(2014, 12, 31)) == 'August 2014'

    assert date_format(date(2014, 7, 31), date(2014, 12, 31)) == 'July 2014'
    assert date_format(date(2014, 1, 31), date(2015, 1, 1)) == 'January 2014'
    assert date_format(date(2014, 1, 31), date(2015, 12, 1)) == 'January 2014'

    assert date_format(date(2015, 1, 31), date(2014, 12, 1)) == 'January'
    assert date_format(date(2015, 3, 31), date(2014, 12, 1)) == 'March'
    assert date_format(date(2015, 4, 30), date(2014, 12, 1)) == 'April 2015'
    assert date_format(date(2015, 1, 31), date(2014, 1, 1)) == 'January 2015'


def test_random_string():
    for n in (-2, -1):
        with pytest.raises(ValueError) as exc:
            random_string(n)
        assert 'Negative lengths are not allowed' in str(exc)

    for n in (1, 1.5, 3, 39):
        with pytest.raises(ValueError) as exc:
            random_string(n)
        assert 'The length must be a multiple of 4' in str(exc)

    for n in (0, 4, 8, 40):
        assert isinstance(random_string(n), type(u''))
        assert len(random_string(n)) == n
