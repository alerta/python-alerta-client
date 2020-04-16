import unittest

import requests_mock

from alertaclient.api import Client


class HeartbeatTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.heartbeat = """
        {
            "heartbeat": {
                "createTime": "2017-10-02T23:54:05.214Z",
                "customer": null,
                "href": "http://localhost:8080/heartbeat/4a0b87cd-9786-48f8-9994-59a9209ff0b2",
                "id": "4a0b87cd-9786-48f8-9994-59a9209ff0b2",
                "latency": 0.0,
                "origin": "app/web01",
                "receiveTime": "2017-10-02T23:54:05.214Z",
                "since": 0,
                "status": "ok",
                "tags": [
                    "london",
                    "linux"
                ],
                "timeout": 10,
                "type": "Heartbeat"
            },
            "id": "4a0b87cd-9786-48f8-9994-59a9209ff0b2",
            "status": "ok"
        }
        """

    @requests_mock.mock()
    def test_heartbeat(self, m):
        m.post('http://localhost:8080/heartbeat', text=self.heartbeat)
        hb = self.client.heartbeat(origin='app/web01', timeout=10, tags=['london', 'linux'])
        self.assertEqual(hb.origin, 'app/web01')
        self.assertEqual(hb.event_type, 'Heartbeat')
        self.assertEqual(hb.timeout, 10)
        self.assertIn('linux', hb.tags)
