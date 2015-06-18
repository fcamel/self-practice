import logging
import json

import tornado.ioloop
import tornado.web
import tornado.locks
import tornado.gen

AUTORELOAD = True


class Entry(object):
    def __init__(self):
        self._condition = None
        self._ngetter = 0
        self._expired = None
        self._value = None

    def get_condition(self):
        if not self._condition:
            self._condition = tornado.locks.Condition()
        self._ngetter += 1
        return self._condition

    def release_condition(self):
        self._ngetter -= 1
        if not self._ngetter:
            self._condition = None

    def get_expired(self):
        return self._expired

    def set_value(self, value, expired):
        self._value = value
        self._expired = expired
        if self._condition:
            self._condition.notify_all()

    def get_value(self):
        return self._value


g_cache = {}

ERROR_OK = 0
ERROR_UNKNOWN_ERROR = 1
ERROR_INVALID_INPUT = 2
ERROR_TIMEOUT = 2


class GetHandler(tornado.web.RequestHandler):
    def error(self, code):
        self.write(json.dumps({'error_code': code}))

    @tornado.gen.coroutine
    def post(self):
        '''
        Return the value of key |key|. Wait for the value for |timeout| seconds.
        If |timeout| is not set, wait forever.
        '''
        global g_cache

        key = self.get_argument("key", None)
        if not key:
            self.error(ERROR_INVALID_INPUT)
            return

        entry = g_cache.get(key, None)
        if not entry:
            entry = g_cache[key] = Entry()

        value = entry.get_value()
        if value is not None:
            self.write(json.dumps({
                'error_code': ERROR_OK,
                'value': value,
            }))
            return

        # Wait the data to be ready.
        timeout = self.get_argument("timeout", None)
        if timeout:
            try:
                timeout = float(timeout)
                if timeout > 0:
                    timeout += tornado.ioloop.IOLoop.current().time()
            except Exception, e:
                logging.exception('timeout is invalid.')
                timeout = None

        condition = entry.get_condition()
        try:
            yield condition.wait(timeout=timeout)  # Yield a Future.
        except Exception, e:
            logging.exception('condition timeout? timeout=%s' % str(timeout))
            entry.release_condition()
            self.error(ERROR_TIMEOUT)
            return

        entry.release_condition()
        value = entry.get_value()
        # NOTE(fcamel): The API doc says a tornado.gen.TimeoutError should be raised
        # if there is no notification. However, it does not raise, so I need to check
        # the value again.
        if value is None:
            self.error(ERROR_TIMEOUT)
            return

        self.write(json.dumps({
            'error_code': ERROR_OK,
            'value': value,
        }))


class SetHandler(tornado.web.RequestHandler):
    def error(self, code):
        self.write(json.dumps({'error_code': code}))

    @tornado.gen.coroutine
    def post(self):
        '''
        Set |value| by |key| and notify all connections waiting |key|'s value.
        |value| will be cleared after the |expired| seconds.
        |expired|'s default value is 86400 seconds.
        '''
        global g_cache

        key = self.get_argument("key", None)
        value = self.get_argument("value", None)
        if not key or not value:
            self.error(ERROR_INVALID_INPUT)
            return
        expired = self.get_argument("expired", 86400)
        try:
            expired = float(expired)
        except Exception, e:
            self.error(ERROR_INVALID_INPUT)
            return;

        entry = g_cache.get(key, None)
        if not entry:
            entry = g_cache[key] = Entry()
        expired += tornado.ioloop.IOLoop.current().time()
        entry.set_value(value, expired)
        self.write(json.dumps({'error_code': ERROR_OK}))

class ClearHandler(tornado.web.RequestHandler):
    def post(self):
        '''
        Clear data before |valid_begin|.
        If |valid_begin| is not set, clear all data.
        '''
        # Clear all.
        global g_cache

        valid_begin = self.get_argument('valid_begin', -1)
        try:
            valid_begin = float(valid_begin)
        except Exception, e:
            logging.exception('invalid valid_begin: %s' % valid_begin)
            self.write(json.dumps({'error_code': ERROR_INVALID_INPUT}))
            return

        keys = g_cache.keys()
        for key in keys:
            expired_time = g_cache[key].get_expired()
            if (valid_begin < 0  # Clear all
                or expired_time < valid_begin):  # Clear partial.
                del g_cache[key]
        self.write(json.dumps({'error_code': ERROR_OK}))


application = tornado.web.Application([
    (r"/get", GetHandler),
    (r"/set", SetHandler),
    (r"/clear", ClearHandler),
], autoreload=AUTORELOAD)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
