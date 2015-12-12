# -*- coding: utf-8 -*-
"""Server-side sessions."""

from datetime import datetime, timedelta
from flask.sessions import SessionInterface, SessionMixin
from json import dumps, loads
from werkzeug.datastructures import CallbackDict
from .util import LazyObject, random_string


class RedisSession(CallbackDict, SessionMixin):
    """The session object."""

    def __init__(self, initial=None, sid=None, new=None):
        def on_update(self):
            self.modified = True
        if initial is None:
            initial = {}
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.old_sid = None
        self.new = new
        self.modified = False

    def init_data(self):
        """Create a random session key and CSRF token."""
        self.sid = random_string(64)
        self['csrf'] = random_string(64)

    def rotate(self):
        """Reset the session key and CSRF token."""
        if not self.new:
            self.old_sid = self.sid
        self.init_data()


class RedisSessionInterface(SessionInterface):

    session_class = RedisSession

    def open_session(self, app, request):
        """Attempt to load the session from a cookie, or create one."""
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            data = app.redis.get(self.redis_key(sid))
            if data:
                initial = loads(data.decode())
                return self.session_class(initial=initial, sid=sid)
        session = self.session_class(new=True)
        session.init_data()
        return session

    def redis_key(self, sid):
        return 'session:{0}'.format(sid)

    def get_session_lifetime(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def get_expiration_time(self, app, session):
        return datetime.utcnow() + self.get_session_lifetime(app, session)

    def save_session(self, app, session, response):
        """Write the session to redis, and set the cookie."""
        domain = self.get_cookie_domain(app)
        if not session:
            app.redis.delete(self.redis_key(session.sid))
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        redis_key = self.redis_key(session.sid)
        redis_exp = self.get_session_lifetime(app, session)
        expire_seconds = redis_exp.days * 60 * 60 * 24 + redis_exp.seconds
        if session.old_sid:
            app.redis.delete(self.redis_key(session.old_sid))
        if session.modified:
            app.redis.setex(redis_key, expire_seconds, dumps(dict(session)))
        else:
            app.redis.expire(redis_key, expire_seconds)

        cookie_exp = self.get_expiration_time(app, session)
        secure = self.get_cookie_secure(app)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True, domain=domain,
                            secure=secure)


class LazyRedisSessionInterface(RedisSessionInterface):

    def open_session(self, *args):
        def callback():
            return super(LazyRedisSessionInterface, self).open_session(*args)
        return LazyObject(callback)

    def save_session(self, app, session, response):
        if session.instantiated:
            super(LazyRedisSessionInterface, self).save_session(app, session,
                                                                response)
