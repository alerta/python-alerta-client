import unittest

import requests_mock

from alertaclient.api import Client


class BlackoutTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.blackout = """
            {
                "blackout": {
                    "createTime": "2018-08-26T20:45:04.622Z",
                    "customer": null,
                    "duration": 3600,
                    "endTime": "2018-08-26T21:45:04.622Z",
                    "environment": "Production",
                    "event": null,
                    "group": null,
                    "href": "http://localhost:8080/blackout/e18a4be8-60d7-4ce2-9b3d-f18d814f7b85",
                    "id": "e18a4be8-60d7-4ce2-9b3d-f18d814f7b85",
                    "priority": 3,
                    "remaining": 3599,
                    "resource": null,
                    "service": [
                        "Network"
                    ],
                    "startTime": "2018-08-26T20:45:04.622Z",
                    "status": "active",
                    "tags": [
                        "london",
                        "linux"
                    ],
                    "text": "Network outage in Bracknell",
                    "user": "admin@alerta.io"
                },
                "id": "e18a4be8-60d7-4ce2-9b3d-f18d814f7b85",
                "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_blackout(self, m):
        m.post('http://localhost:8080/blackout', text=self.blackout)
        alert = self.client.create_blackout(environment='Production', service=[
                                            'Web', 'App'], resource='web01', event='node_down', group='Network', tags=['london', 'linux'])
        self.assertEqual(alert.environment, 'Production')
        self.assertEqual(alert.service, ['Network'])
        self.assertIn('london', alert.tags)
        self.assertEqual(alert.text, 'Network outage in Bracknell')
        self.assertEqual(alert.user, 'admin@alerta.io')
