import unittest

import requests_mock

from alertaclient.api import Client


class FormatsTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.alert = """
            {
                "alert": {
                  "attributes": {
                    "ip": "127.0.0.1"
                  },
                  "correlate": [],
                  "createTime": "2018-04-08T19:01:44.979Z",
                  "customer": null,
                  "duplicateCount": 0,
                  "environment": "Development",
                  "event": "foo",
                  "group": "Misc",
                  "history": [
                    {
                      "event": "foo",
                      "href": "https://alerta-api.herokuapp.com/alert/d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                      "id": "d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                      "severity": null,
                      "status": "shelved",
                      "text": "shelved by Test90",
                      "type": "status",
                      "updateTime": "2018-04-09T09:11:43.502Z",
                      "value": null
                    },
                    {
                      "event": "foo",
                      "href": "https://alerta-api.herokuapp.com/alert/d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                      "id": "d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                      "severity": null,
                      "status": "open",
                      "text": "bulk status change via console by test",
                      "type": "status",
                      "updateTime": "2018-04-24T17:52:40.088Z",
                      "value": null
                    },
                    {
                      "event": "foo",
                      "href": "https://alerta-api.herokuapp.com/alert/d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                      "id": "d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                      "severity": "minor",
                      "status": "shelved",
                      "text": "status change via console by Scott Wenzel",
                      "type": "action",
                      "updateTime": "2018-05-18T03:38:50.333Z",
                      "value": null
                    }
                  ],
                  "href": "https://alerta-api.herokuapp.com/alert/d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                  "id": "d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                  "lastReceiveId": "d1bb37cf-e976-429e-96f5-82b2a48aa50b",
                  "lastReceiveTime": "2018-04-08T19:01:46.090Z",
                  "origin": "alertad/fdaa33ca.lan",
                  "previousSeverity": "indeterminate",
                  "rawData": null,
                  "receiveTime": "2018-04-08T19:01:46.090Z",
                  "repeat": false,
                  "resource": "quux",
                  "service": [
                    "Bar"
                  ],
                  "severity": "minor",
                  "status": "shelved",
                  "tags": [
                    "watch:Scott Wenzel"
                  ],
                  "text": "",
                  "timeout": 3600,
                  "trendIndication": "moreSevere",
                  "type": "exceptionAlert",
                  "value": null
                }
            }
        """

    @requests_mock.mock()
    def test_alert(self, m):
        m.post('http://localhost:8080/alert', text=self.alert)
        msg = {'event': 'foo', 'service': ['Bar']}

        id, alert, message = self.client.send_alert(
            environment='Production',
            resource='quux',
            **msg
        )
        alert_summary = alert.tabular(fields='summary', timezone='UTC')
        self.assertEqual(alert_summary['id'], 'd1bb37cf')

        alert_summary = alert.tabular(fields='details', timezone='UTC')
        self.assertEqual(alert_summary['severity'], 'indeterminate -> minor')

        alert_summary = alert.tabular(fields='all', timezone='UTC')
        self.assertEqual(alert_summary['history'][0]['status'], 'shelved')