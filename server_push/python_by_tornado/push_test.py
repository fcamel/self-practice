#!/usr/bin/env python
# -*- encoding: utf8 -*-

import datetime
import json
import logging
import time
import unittest
import urllib

import tornado
import tornado.httpclient

import push


def to_json(text):
    try:
        return json.loads(text)
    except Exception, e:
        return {}


class PushTest(unittest.TestCase):
    def setUp(self):
        self.url = 'http://localhost:8888'
        self.responses = []
        tornado.ioloop.IOLoop.current().add_timeout(
            datetime.timedelta(milliseconds=500),
            tornado.ioloop.IOLoop.current().stop)

    def tearDown(self):
        self._send_http_request(self.url + '/clear', {}, stop_after_done=True)
        tornado.ioloop.IOLoop.current().start()

    def _send_http_request(self, url, data, stop_after_done=False):
        try:
            body = urllib.urlencode(data)
            client = tornado.httpclient.AsyncHTTPClient()
            client.fetch(url, self._handle_request, method='POST', body=body)
        except Exception, e:
            logging.exception('url=%s' % url)

        if stop_after_done:
            tornado.ioloop.IOLoop.current().stop()

    def _handle_request(self, response):
        self.responses.append(response)

    def testGetWithExistedData(self):
        # Set first.
        key = 'abc'
        value = 'hello'
        data = {
            'key': key,
            'value': value
        }
        self._send_http_request(self.url + '/set', data)

        # Get latter.
        data = {
            'key': key,
        }
        self._send_http_request(self.url + '/get', data)

        # Run the codes.
        tornado.ioloop.IOLoop.current().start()

        # Verify responses.
        self.assertEquals(2, len(self.responses))
        self.assertEquals(200, self.responses[0].code)
        self.assertEquals(200, self.responses[1].code)
        actual = to_json(self.responses[1].body)
        expected = {
            'error_code': push.ERROR_OK,
            'value': value,
        }
        self.assertEquals(expected, actual)

    def testCannotGetExpiredValue(self):
        # Set first.
        key = 'some_key'
        value = 'some_value'
        data = {
            'key': key,
            'value': value,
            'expired': -1,
        }
        self._send_http_request(self.url + '/set', data)

        # Get latter.
        data = {
            'key': key,
            'timeout': 0.1,
        }
        self._send_http_request(self.url + '/get', data)

        # Run the codes.
        tornado.ioloop.IOLoop.current().start()

        # Verify responses.
        self.assertEquals(2, len(self.responses))
        self.assertEquals(200, self.responses[0].code)
        self.assertEquals(200, self.responses[1].code)
        actual = to_json(self.responses[1].body)
        expected = {
            'error_code': push.ERROR_TIMEOUT,
        }
        self.assertEquals(expected, actual)

    def testGetWithTimeout(self):
        key = 'not_exist'
        data = {
            'key': key,
            'timeout': 0.1,
        }
        self._send_http_request(self.url + '/get', data)

        tornado.ioloop.IOLoop.current().start()

        self.assertEquals(1, len(self.responses))
        self.assertEquals(200, self.responses[0].code)
        actual = to_json(self.responses[0].body)
        expected = {
            'error_code': push.ERROR_TIMEOUT,
        }
        self.assertEquals(expected, actual)

    def testGetBeforeSet(self):
        key = 'not_exist_yet'
        value = 'camel'

        # Get first.
        data = {
            'key': key,
            'timeout': 1.0,
        }
        self._send_http_request(self.url + '/get', data)
        self._send_http_request(self.url + '/get', data)

        # Set latter.
        data = {
            'key': key,
            'value': value,
        }
        r = self._send_http_request(self.url + '/set', data)

        # Run it.
        tornado.ioloop.IOLoop.current().start()

        # Verify.
        # Set is done first.
        self.assertEquals(3, len(self.responses))
        for i in range(3):
            self.assertEquals(200, self.responses[i].code)
        expected = {
            'error_code': push.ERROR_OK,
            'value': value,
        }
        self.assertEquals(expected, to_json(self.responses[1].body))
        self.assertEquals(expected, to_json(self.responses[2].body))

    def testClearExpired(self):
        valid_begin = tornado.ioloop.IOLoop.current().time()
        # Set two values.
        key = 'lala'
        key2 = 'expired_key'
        data = {
            'key': key,
            'value': key,
            'expired': 10.0,
        }
        self._send_http_request(self.url + '/set', data)
        data = {
            'key': key2,
            'value': key2,
            'expired': -1
        }

        # Clear the expired value.
        self._send_http_request(self.url + '/set', data)
        data = {
            'valid_begin': valid_begin,
        }
        self._send_http_request(self.url + '/clear', data)

        # Get the two values.
        data = {
            'key': key,
            'timeout': 0.1
        }
        self._send_http_request(self.url + '/get', data)
        data = {
            'key': key2,
            'timeout': 0.1
        }
        self._send_http_request(self.url + '/get', data)

        # Run it.
        tornado.ioloop.IOLoop.current().start()

        # Verify.
        self.assertEquals(5, len(self.responses))
        for i in range(5):
            self.assertEquals(200, self.responses[i].code)
        expected = {
            'error_code': push.ERROR_OK,
            'value': key,
        }
        self.assertEquals(expected, to_json(self.responses[-2].body))
        expected = {
            'error_code': push.ERROR_TIMEOUT,
        }
        self.assertEquals(expected, to_json(self.responses[-1].body))


if __name__ == '__main__':
    unittest.main()
