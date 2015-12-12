# -*- coding: utf-8 -*-
"""Test session."""

from expenses.session import LazyRedisSessionInterface
import fakeredis
import flask
import json
import pytest


@pytest.fixture
def client():
    db = fakeredis.FakeStrictRedis()
    db.hmset('session:abcd', {
        'csrf': 'somecsrf',
        'a': 'b',
    })

    app = flask.Flask(__name__)
    app.debug = True
    app.redis = db
    app.session_interface = LazyRedisSessionInterface()

    @app.route('/lazy')
    def lazy():
        return 'No sessions used'

    @app.route('/')
    def home():
        return flask.jsonify({
            'data': dict(flask.session),
            'sid': flask.session.sid,
        })

    @app.route('/update', methods=['PUT'])
    def update():
        for k, v in flask.request.get_json().items():
            flask.session[k] = v
        return home()

    @app.route('/logout', methods=['POST'])
    def logout():
        flask.session.clear()
        return home()

    @app.route('/permanent', methods=['POST'])
    def permanent():
        flask.session.permanent = True
        return home()

    @app.route('/rotate', methods=['POST'])
    def rotate():
        flask.session.rotate()
        return home()

    return app.test_client()


def test_lazy(client, monkeypatch):

    def should_not_run():
        raise AssertionError("This shouldn't run")
    monkeypatch.setattr('expenses.session.RedisSessionInterface.open_session',
                        should_not_run)
    monkeypatch.setattr('expenses.session.RedisSessionInterface.save_session',
                        should_not_run)

    rv = client.get('/lazy')
    assert rv.data == b'No sessions used'
    assert 'session=' not in rv.headers.get('Cookie', '')


def test_new_session(client):
    rv = client.get('/')
    data = json.loads(rv.data.decode())
    sid = data['sid']
    assert len(sid) == 64
    assert len(data['data']) == 1
    csrf = data['data']['csrf']
    assert len(csrf) == 64
    assert rv.status_code == 200

    # Check that this new session persists
    rv = client.get('/')
    data = json.loads(rv.data.decode())
    assert data['sid'] == sid
    assert len(data['data']) == 1
    assert data['data']['csrf'] == csrf
    assert rv.status_code == 200


def test_permanent_session(client):
    rv = client.post('/permanent')
    data = json.loads(rv.data.decode())
    assert data['data']['_permanent'] == True


def test_existing_session(client):
    client.set_cookie('localhost', 'session', 'abcd')
    rv = client.get('/')
    data = json.loads(rv.data.decode())
    assert data['sid'] == 'abcd'
    assert data['data'] == {
        'a': 'b',
        'csrf': 'somecsrf',
    }
    assert rv.status_code == 200


def test_invalid_session(client):
    client.set_cookie('localhost', 'session', 'fake')
    rv = client.get('/')
    data = json.loads(rv.data.decode())
    assert data['sid'] != 'fake'
    assert len(data['sid']) == 64
    assert len(data['data']['csrf']) == 64
    assert 'session=' + data['sid'] in rv.headers['Set-Cookie']
    assert rv.status_code == 200


def test_change_session(client):
    client.set_cookie('localhost', 'session', 'abcd')
    headers = {
        'Content-Type': 'application/json',
    }
    rv = client.put('/update', headers=headers, data='{"csrf":"abc","a":"c"}')
    data = json.loads(rv.data.decode())
    assert data['sid'] == 'abcd'
    assert data['data'] == {
        'csrf': 'abc',
        'a': 'c',
    }
    assert client.application.redis.hgetall('session:abcd') == {
        b'csrf': b'abc',
        b'a': b'c',
    }


def test_delete_session(client):
    client.set_cookie('localhost', 'session', 'abcd')
    rv = client.post('/logout')
    data = json.loads(rv.data.decode())
    assert data['sid'] == 'abcd'
    assert data['data'] == {}
    assert client.application.redis.hgetall('session:abcd') == {}
    assert 'Expires=Thu, 01-Jan-1970 00:00:00 GMT' in rv.headers['Set-Cookie']


def test_rotate_session(client):
    client.set_cookie('localhost', 'session', 'abcd')
    rv = client.post('/rotate')
    data = json.loads(rv.data.decode())

    assert len(data['sid']) == 64
    assert 'session={0}'.format(data['sid']) in rv.headers['Set-Cookie']
    assert len(data['data']['csrf']) == 64
    assert data['data']['a'] == 'b'
    assert client.application.redis.exists('session:abcd') == False

    db_d = client.application.redis.hgetall('session:{0}'.format(data['sid']))
    assert len(db_d[b'csrf']) == 64
    assert db_d[b'a'] == b'b'


def test_rotate_new_session(client):
    client.set_cookie('localhost', 'session', 'abcd')
    rv = client.post('/rotate')
    data = json.loads(rv.data.decode())

    assert len(data['sid']) == 64
    assert 'session={0}'.format(data['sid']) in rv.headers['Set-Cookie']
    assert len(data['data']['csrf']) == 64
    assert data['data']['a'] == 'b'

    db_d = client.application.redis.hgetall('session:{0}'.format(data['sid']))
    assert len(db_d[b'csrf']) == 64
    assert db_d[b'a'] == b'b'
