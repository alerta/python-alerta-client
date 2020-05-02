import unittest

import requests_mock

from alertaclient.api import HTTPClient


class HttpClientTestCase(unittest.TestCase):

    def setUp(self):
        self.http = HTTPClient(endpoint='https://httpbin.org')

    @requests_mock.mock()
    def test_query_string(self, m):

        m.get('https://httpbin.org/get', text='{}')
        m.post('https://httpbin.org/post', text='{}')
        m.put('https://httpbin.org/put', text='{}')
        m.delete('https://httpbin.org/delete', text='{}')

        self.http.get(path='/get', query=None)
        self.http.get(path='/get', query=(('foo', 'bar'), ('quxx', 'baz')))
        self.http.get(path='/get', query=None, page=None)
        self.http.get(path='/get', query=None, page=2, page_size=None)
        self.http.get(path='/get', query=None, page=None, page_size=None)
        self.http.get(path='/get', query=None, page=2, page_size=100)
        self.http.get(path='/get', query=None, page_size=20)
        self.http.get(path='/get', query=None, page=None, page_size=200)

        history = m.request_history
        self.assertEqual(history[0].url, 'https://httpbin.org/get')
        self.assertEqual(history[1].url, 'https://httpbin.org/get?foo=bar&quxx=baz')
        self.assertEqual(history[2].url, 'https://httpbin.org/get?page=1')
        self.assertEqual(history[3].url, 'https://httpbin.org/get?page=2&page-size=50')
        self.assertEqual(history[4].url, 'https://httpbin.org/get?page=1&page-size=50')
        self.assertEqual(history[5].url, 'https://httpbin.org/get?page=2&page-size=100')
        self.assertEqual(history[6].url, 'https://httpbin.org/get?page-size=20')
        self.assertEqual(history[7].url, 'https://httpbin.org/get?page=1&page-size=200')

        self.http.post(path='/post', data='{}')
        self.assertEqual(history[8].url, 'https://httpbin.org/post')

        self.http.put(path='/put', data='{}')
        self.assertEqual(history[9].url, 'https://httpbin.org/put')

        self.http.delete(path='/delete')
        self.assertEqual(history[10].url, 'https://httpbin.org/delete')
