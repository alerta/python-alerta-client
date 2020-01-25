import unittest

import requests_mock

from alertaclient.api import Client


class HistoryTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.history = """
            {
                "history": [
                    {
                        "attributes": {
                            "ip": "127.0.0.1",
                            "notify": false
                        },
                        "customer": null,
                        "environment": "Production",
                        "event": "node_down",
                        "group": "Misc",
                        "href": "http://localhost:8080/alert/e7020428-5dad-4a41-9bfe-78e9d55cda06",
                        "id": "e7020428-5dad-4a41-9bfe-78e9d55cda06",
                        "origin": "alertad/fdaa33ca.local",
                        "resource": "web01",
                        "service": [
                            "Web",
                            "App"
                        ],
                        "severity": "critical",
                        "tags": [
                            "london",
                            "linux"
                        ],
                        "text": "",
                        "type": "severity",
                        "updateTime": "2017-10-03T09:12:27.283Z",
                        "value": "4"
                    }
                ],
                "status": "ok",
                "total": 1
            }
        """

    @requests_mock.mock()
    def test_history(self, m):
        m.get('http://localhost:8080/alerts/history', text=self.history)
        hist = self.client.get_history()
        self.assertEqual(hist[0].environment, 'Production')
        self.assertEqual(hist[0].service, ['Web', 'App'])
        self.assertEqual(hist[0].resource, 'web01')
        self.assertIn('london', hist[0].tags)
        self.assertEqual(hist[0].change_type, 'severity')
