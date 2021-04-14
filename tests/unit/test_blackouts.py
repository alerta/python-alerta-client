import unittest

import requests_mock

from alertaclient.api import Client


class BlackoutTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.blackout = """
            {
                "blackout": {
                    "createTime": "2021-04-14T20:36:06.453Z",
                    "customer": null,
                    "duration": 3600,
                    "endTime": "2021-04-14T21:36:06.453Z",
                    "environment": "Production",
                    "event": "node_down",
                    "group": "Network",
                    "href": "http://local.alerta.io:8080/blackout/5ed223a3-27dc-4c4c-97d1-504f107d8a1a",
                    "id": "5ed223a3-27dc-4c4c-97d1-504f107d8a1a",
                    "origin": "foo/xyz",
                    "priority": 8,
                    "remaining": 3600,
                    "resource": "web01",
                    "service": [
                      "Web",
                      "App"
                    ],
                    "startTime": "2021-04-14T20:36:06.453Z",
                    "status": "active",
                    "tags": [
                      "london",
                      "linux"
                    ],
                    "text": "Network outage in Bracknell",
                    "user": "admin@alerta.dev"
                },
                "id": "5ed223a3-27dc-4c4c-97d1-504f107d8a1a",
                "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_blackout(self, m):
        m.post('http://localhost:8080/blackout', text=self.blackout)
        alert = self.client.create_blackout(environment='Production', service=['Web', 'App'], resource='web01',
                                            event='node_down', group='Network', tags=['london', 'linux'],
                                            origin='foo/xyz', text='Network outage in Bracknell')
        self.assertEqual(alert.environment, 'Production')
        self.assertEqual(alert.service, ['Web', 'App'])
        self.assertEqual(alert.group, 'Network')
        self.assertIn('london', alert.tags)
        self.assertEqual(alert.origin, 'foo/xyz')
        self.assertEqual(alert.text, 'Network outage in Bracknell')
        self.assertEqual(alert.user, 'admin@alerta.dev')
