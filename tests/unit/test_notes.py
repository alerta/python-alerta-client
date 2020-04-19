import unittest

import requests_mock

from alertaclient.api import Client


class NotesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.note = """
            {
                "id": "62b62c6c-fca3-4329-b517-fc47c2371e63",
                "note": {
                    "attributes": {
                        "environment": "Production",
                        "event": "node_down",
                        "resource": "web01",
                        "severity": "major",
                        "status": "open"
                    },
                    "createTime": "2020-04-19T10:45:49.385Z",
                    "customer": null,
                    "href": "http://localhost:8080/note/62b62c6c-fca3-4329-b517-fc47c2371e63",
                    "id": "62b62c6c-fca3-4329-b517-fc47c2371e63",
                    "related": {
                        "alert": "e7020428-5dad-4a41-9bfe-78e9d55cda06"
                    },
                    "text": "this is a new note",
                    "type": "alert",
                    "updateTime": null,
                    "user": null
                },
                "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_add_note(self, m):
        m.put('http://localhost:8080/alert/e7020428-5dad-4a41-9bfe-78e9d55cda06/note', text=self.note)
        note = self.client.alert_note(id='e7020428-5dad-4a41-9bfe-78e9d55cda06', text='this is a new note')
        self.assertEqual(note.text, 'this is a new note')
