
import unittest

import requests_mock

from alertaclient.api import Client

try:
    from unittest import mock
except ImportError:
    import mock


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.alert = """
        {
            "alert": {
                "attributes": {
                    "ip": "127.0.0.1"
                },
                "correlate": [],
                "createTime": "2017-10-02T23:51:10.748Z",
                "customer": null,
                "duplicateCount": 0,
                "environment": "Production",
                "event": "node_down",
                "group": "Misc",
                "history": [
                    {
                        "event": "node_down",
                        "href": "http://localhost:8080/alert/f12a96f5-64a3-4aaa-aaaa-1f3ffe2078e5",
                        "id": "f12a96f5-64a3-4aaa-aaaa-1f3ffe2078e5",
                        "severity": "critical",
                        "status": null,
                        "text": "",
                        "type": "severity",
                        "updateTime": "2017-10-02T23:51:10.748Z",
                        "value": null
                    }
                ],
                "href": "http://localhost:8080/alert/f12a96f5-64a3-4aaa-aaaa-1f3ffe2078e5",
                "id": "f12a96f5-64a3-4aaa-aaaa-1f3ffe2078e5",
                "lastReceiveId": "f12a96f5-64a3-4aaa-aaaa-1f3ffe2078e5",
                "lastReceiveTime": "2017-10-02T23:51:10.750Z",
                "origin": "alertad/fdaa33ca.home",
                "previousSeverity": "indeterminate",
                "rawData": null,
                "receiveTime": "2017-10-02T23:51:10.750Z",
                "repeat": false,
                "resource": "web01",
                "service": [
                    "Web",
                    "App"
                ],
                "severity": "critical",
                "status": "open",
                "tags": [
                    "london",
                    "linux"
                ],
                "text": "",
                "timeout": 86400,
                "trendIndication": "moreSevere",
                "type": "exceptionAlert",
                "value": "4"
            },
            "id": "f12a96f5-64a3-4aaa-aaaa-1f3ffe2078e5",
            "status": "ok"
        }
        """

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
    def test_alert(self, m):
        m.post('http://localhost:8080/alert', text=self.alert)
        alert = self.client.send_alert(resource='web01', event='node_down', tags=["london", "linux"], value=4)
        self.assertEqual(alert.value, "4")  # values cast to string
        self.assertIn("london", alert.tags)

    @requests_mock.mock()
    def test_heartbeat(self, m):
        m.post('http://localhost:8080/heartbeat', text=self.heartbeat)
        hb = self.client.heartbeat(origin='app/web01', timeout=10, tags=["london", "linux"])
        self.assertEqual(hb.origin, 'app/web01')
        self.assertEqual(hb.event_type, 'Heartbeat')
        self.assertEqual(hb.timeout, 10)
        self.assertIn("linux", hb.tags)
