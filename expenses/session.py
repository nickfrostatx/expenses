# -*- coding: utf-8 -*-
"""Server-side sessions."""

from datetime import datetime, timedelta
from flask.sessions import SessionInterface, SessionMixin
from .util import random_string


class RedisSession(dict, SessionMixin):
    """The session object."""

    def __init__(self, initial=None, sid=None, new=None):
        if initial is None:
            initial = {}
        dict.__init__(self, initial)
        self.sid = sid
        self.old_sid = None
        self.new = new
        self.modified_keys = set()

    def init_data(self):
        """Create a random session key and CSRF token."""
        self.sid = random_string(64)
        self['csrf'] = random_string(64)

    def rotate(self):
        """Reset the session key and CSRF token."""
        if not self.new:
            self.old_sid = self.sid
        self.init_data()

    def __setitem__(self, key, value):
        """Change the value, and record the change."""
        self.modified = True
        self.modified_keys.add(key)
        return super(RedisSession, self).__setitem__(key, value)


class RedisSessionInterface(SessionInterface):

    session_class = RedisSession

    def open_session(self, app, request):
        """Attempt to load the session from a cookie, or create one."""
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
                data = app.redis.hgetall(self.redis_key(sid))
                if data:
                    initial = {}
                    for d in data:
                        initial[d.decode()] = data[d].decode()
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
        changed_data = dict((k, session.get(k)) for k in session.modified_keys)
        if session.old_sid:
            app.redis.rename(self.redis_key(session.old_sid), redis_key)
        if changed_data:
            app.redis.hmset(redis_key, changed_data)
        app.redis.expire(redis_key, expire_seconds)

        cookie_exp = self.get_expiration_time(app, session)
        secure = self.get_cookie_secure(app)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True, domain=domain,
                            secure=secure)
