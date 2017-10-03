
import unittest

import requests_mock

from alertaclient.api import Client


class BlackoutTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.blackout = """
            {
              "blackout": {
                "customer": null,
                "duration": 300,
                "endTime": "2017-10-03T08:26:00.948Z",
                "environment": "Production",
                "event": "node_down",
                "group": "Network",
                "href": "http://localhost:8080/blackout/8eb1504f-cb48-433d-854c-b31e06284af9",
                "id": "8eb1504f-cb48-433d-854c-b31e06284af9",
                "priority": 3,
                "remaining": 299,
                "resource": "web01",
                "service": [
                  "Web",
                  "App"
                ],
                "startTime": "2017-10-03T08:21:00.948Z",
                "status": "active",
                "tags": [
                  "london",
                  "linux"
                ]
              },
              "id": "8eb1504f-cb48-433d-854c-b31e06284af9",
              "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_blackout(self, m):
        m.post('http://localhost:8080/blackout', text=self.blackout)
        alert = self.client.create_blackout(environment='Production', service=['Web', 'App'], resource='web01', event='node_down', group='Network', tags=["london", "linux"])
        self.assertEqual(alert.environment, 'Production')
        self.assertEqual(alert.service, ['Web', 'App'])
        self.assertEqual(alert.resource, 'web01')
        self.assertIn("london", alert.tags)
