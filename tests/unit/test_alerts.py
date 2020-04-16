import unittest

import requests_mock

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.alert = """
            {
              "alert": {
                "attributes": {
                  "ip": "127.0.0.1",
                  "notify": false
                },
                "correlate": [],
                "createTime": "2017-10-03T09:12:27.283Z",
                "customer": null,
                "duplicateCount": 4,
                "environment": "Production",
                "event": "node_down",
                "group": "Misc",
                "history": [],
                "href": "http://localhost:8080/alert/e7020428-5dad-4a41-9bfe-78e9d55cda06",
                "id": "e7020428-5dad-4a41-9bfe-78e9d55cda06",
                "lastReceiveId": "534ced13-ddb0-435e-8f94-a38691719683",
                "lastReceiveTime": "2017-10-03T09:15:06.156Z",
                "origin": "alertad/fdaa33ca.local",
                "previousSeverity": "indeterminate",
                "rawData": null,
                "receiveTime": "2017-10-03T09:12:27.289Z",
                "repeat": true,
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
              "id": "e7020428-5dad-4a41-9bfe-78e9d55cda06",
              "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_alert(self, m):
        m.post('http://localhost:8080/alert', text=self.alert)
        id, alert, message = self.client.send_alert(
            environment='Production', resource='web01', event='node_down', correlated=['node_up', 'node_down'],
            service=['Web', 'App'], severity='critical', tags=['london', 'linux'], value=4
        )
        self.assertEqual(alert.value, '4')  # values cast to string
        self.assertEqual(alert.timeout, 86400)  # timeout returned as int
        self.assertIn('london', alert.tags)
