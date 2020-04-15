import unittest

import requests_mock

from alertaclient.api import Client


class NotesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.note = """
            {
              "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_add_note(self, m):
        m.put('http://localhost:8080/alert/e7020428-5dad-4a41-9bfe-78e9d55cda06/note', text=self.note)
        r = self.client.alert_note(id='e7020428-5dad-4a41-9bfe-78e9d55cda06', note='this is a test note')
        self.assertEqual(r['status'], 'ok')
