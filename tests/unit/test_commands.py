import unittest
from uuid import UUID

import requests_mock
from click.testing import CliRunner

from alertaclient.api import Client
from alertaclient.commands.cmd_heartbeat import cli as heartbeat_cmd
from alertaclient.commands.cmd_heartbeats import cli as heartbeats_cmd
from alertaclient.commands.cmd_whoami import cli as whoami_cmd
from alertaclient.config import Config


class CommandsTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        alarm_model = {
            'name': 'Alerta 8.0.1',
            'severity': {
                'security': 0,
                'critical': 1,
                'major': 2,
                'minor': 3,
                'warning': 4,
                'indeterminate': 5,
                'informational': 6,
                'normal': 7,
                'ok': 7,
                'cleared': 7,
                'debug': 8,
                'trace': 9,
                'unknown': 10
            },
            'defaults': {
                'normal_severity': 'normal'
            }
        }

        config = Config(config_file=None, config_override={'alarm_model': alarm_model})
        self.obj = config.options
        self.obj['client'] = self.client

        self.runner = CliRunner(echo_stdin=True)

    @requests_mock.mock()
    def test_heartbeat_cmd(self, m):

        heartbeat_response = """
        {
          "heartbeat": {
            "attributes": {
              "environment": "Production",
              "service": [
                "Web"
              ],
              "severity": "major"
            },
            "createTime": "2020-01-25T12:32:50.223Z",
            "customer": null,
            "href": "http://api.local.alerta.io:8080/heartbeat/e07d7c02-0b41-418a-b0e6-cd172e06c872",
            "id": "e07d7c02-0b41-418a-b0e6-cd172e06c872",
            "latency": 14,
            "maxLatency": 2000,
            "origin": "alerta/macbook.lan",
            "receiveTime": "2020-01-25T12:32:50.237Z",
            "since": 0,
            "status": "ok",
            "tags": [],
            "timeout": 86400,
            "type": "Heartbeat"
          },
          "id": "e07d7c02-0b41-418a-b0e6-cd172e06c872",
          "status": "ok"
        }
        """

        m.post('/heartbeat', text=heartbeat_response)
        result = self.runner.invoke(heartbeat_cmd, ['-E', 'Production', '-S', 'Web', '-s', 'major'], obj=self.obj)
        UUID(result.output.strip())
        self.assertEqual(result.exit_code, 0)

    @requests_mock.mock()
    def test_heartbeats_cmd(self, m):

        heartbeats_response = """
        {
          "heartbeats": [
            {
              "attributes": {
                "environment": "Infrastructure",
                "severity": "major",
                "service": ["Internal"],
                "group": "Heartbeats",
                "region": "EU"
              },
              "createTime": "2020-03-10T20:25:54.541Z",
              "customer": null,
              "href": "http://127.0.0.1/heartbeat/52c202e8-d949-45ed-91e0-cdad4f37de73",
              "id": "52c202e8-d949-45ed-91e0-cdad4f37de73",
              "latency": 0,
              "maxLatency": 2000,
              "origin": "monitoring-01",
              "receiveTime": "2020-03-10T20:25:54.541Z",
              "since": 204,
              "status": "expired",
              "tags": [],
              "timeout": 90,
              "type": "Heartbeat"
            }
          ],
          "status": "ok",
          "total": 1
        }
        """

        heartbeat_alert_response = """
        {
          "alert": {
            "attributes": {},
            "correlate": [
              "HeartbeatFail",
              "HeartbeatSlow",
              "HeartbeatOK"
            ],
            "createTime": "2020-03-10T21:55:07.884Z",
            "customer": null,
            "duplicateCount": 0,
            "environment": "Infrastructure",
            "event": "HeartbeatSlow",
            "group": "Heartbeat",
            "history": [
              {
                "event": "HeartbeatSlow",
                "href": "http://api.local.alerta.io:8080/alert/6cfbc30f-c2d6-4edf-b672-841070995206",
                "id": "6cfbc30f-c2d6-4edf-b672-841070995206",
                "severity": "warning",
                "status": "open",
                "text": "new alert",
                "type": "new",
                "updateTime": "2020-03-10T21:55:07.884Z",
                "user": null,
                "value": "22ms"
              }
            ],
            "href": "http://api.local.alerta.io:8080/alert/6cfbc30f-c2d6-4edf-b672-841070995206",
            "id": "6cfbc30f-c2d6-4edf-b672-841070995206",
            "lastReceiveId": "6cfbc30f-c2d6-4edf-b672-841070995206",
            "lastReceiveTime": "2020-03-10T21:55:07.916Z",
            "origin": "alerta/macbook.lan",
            "previousSeverity": "indeterminate",
            "rawData": null,
            "receiveTime": "2020-03-10T21:55:07.916Z",
            "repeat": false,
            "resource": "monitoring-01",
            "service": [
              "Internal"
            ],
            "severity": "warning",
            "status": "open",
            "tags": [],
            "text": "Heartbeat took more than 2ms to be processed",
            "timeout": 86000,
            "trendIndication": "moreSevere",
            "type": "heartbeatAlert",
            "updateTime": "2020-03-10T21:55:07.916Z",
            "value": "22ms"
          },
          "id": "6cfbc30f-c2d6-4edf-b672-841070995206",
          "status": "ok"
        }
        """

        m.get('/heartbeats', text=heartbeats_response)
        m.post('/alert', text=heartbeat_alert_response)
        result = self.runner.invoke(heartbeats_cmd, ['--alert'], obj=self.obj)
        self.assertEqual(result.exit_code, 0, result.exception)
        self.assertIn('monitoring-01', result.output)

        history = m.request_history
        data = history[1].json()
        self.assertEqual(data['environment'], 'Infrastructure')
        self.assertEqual(data['severity'], 'major')
        self.assertEqual(data['service'], ['Internal'])
        self.assertEqual(data['group'], 'Heartbeats')
        self.assertEqual(data['attributes'], {'region': 'EU'})

    @requests_mock.mock()
    def test_whoami_cmd(self, m):

        whoami_response = """
        {
          "aud": "736147134702-glkb1pesv716j1utg4llg7c3rr7nnhli.apps.googleusercontent.com",
          "customers": [],
          "email": "admin@alerta.io",
          "exp": 1543264150,
          "iat": 1542054550,
          "iss": "https://alerta-api.herokuapp.com/",
          "jti": "54bfe4fd-5ed3-4d43-abc5-09cea407af94",
          "name": "admin@alerta.io",
          "nbf": 1542054550,
          "preferred_username": "admin@alerta.io",
          "provider": "basic",
          "roles": [
            "admin"
          ],
          "scope": "admin read write",
          "sub": "df97c902-9b66-42f1-97b8-efb37ad942d6"
        }
        """

        m.get('/userinfo', text=whoami_response)
        result = self.runner.invoke(whoami_cmd, ['-u'], obj=self.obj)
        self.assertIn('preferred_username  : admin@alerta.io', result.output)
        self.assertEqual(result.exit_code, 0)
