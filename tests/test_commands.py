import unittest

import requests_mock
from click.testing import CliRunner

from alertaclient.api import Client
from alertaclient.commands.cmd_send import cli as send
from alertaclient.commands.cmd_whoami import cli as whoami
from alertaclient.config import Config


class CommandsTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        config = Config(config_file=None)
        self.obj = config.options
        self.obj['client'] = self.client

        self.runner = CliRunner()

    @requests_mock.mock()
    def test_send_cmd(self, m):

        send_response = """
        {
          "alert": {
            "attributes": {},
            "correlate": [],
            "createTime": "2020-01-17T23:23:31.441Z",
            "customer": null,
            "duplicateCount": 10,
            "environment": "Development",
            "event": "node_down",
            "group": "Misc",
            "history": [
              {
                "event": "node_down",
                "href": "https://alerta-api.herokuapp.com/alert/cca2053f-806d-478c-abb3-bbec6fddbb49",
                "id": "cca2053f-806d-478c-abb3-bbec6fddbb49",
                "severity": "major",
                "status": "open",
                "text": "new alert",
                "type": "new",
                "updateTime": "2020-01-17T23:23:31.441Z",
                "user": "admin@alerta.io",
                "value": null
              },
              {
                "event": "node_down",
                "href": "https://alerta-api.herokuapp.com/alert/cca2053f-806d-478c-abb3-bbec6fddbb49",
                "id": "cca2053f-806d-478c-abb3-bbec6fddbb49",
                "severity": "major",
                "status": "shelved",
                "text": "",
                "type": "shelve",
                "updateTime": "2020-01-18T02:31:56.863Z",
                "user": null,
                "value": null
              },
              {
                "event": "node_down",
                "href": "https://alerta-api.herokuapp.com/alert/cca2053f-806d-478c-abb3-bbec6fddbb49",
                "id": "cca2053f-806d-478c-abb3-bbec6fddbb49",
                "severity": "major",
                "status": "open",
                "text": "",
                "type": "unshelve",
                "updateTime": "2020-01-18T02:33:41.863Z",
                "user": null,
                "value": null
              },
              {
                "event": "node_down",
                "href": "https://alerta-api.herokuapp.com/alert/cca2053f-806d-478c-abb3-bbec6fddbb49",
                "id": "cca2053f-806d-478c-abb3-bbec6fddbb49",
                "severity": "major",
                "status": "ack",
                "text": "",
                "type": "ack",
                "updateTime": "2020-01-18T02:33:49.536Z",
                "user": null,
                "value": null
              }
            ],
            "href": "https://alerta-api.herokuapp.com/alert/cca2053f-806d-478c-abb3-bbec6fddbb49",
            "id": "cca2053f-806d-478c-abb3-bbec6fddbb49",
            "lastReceiveId": "c3d6a74a-e346-4293-a44c-f6b3465e8732",
            "lastReceiveTime": "2020-01-18T12:58:24.100Z",
            "origin": "gunicorn/47e463df-f3db-4786-93e6-1d4f029666b3",
            "previousSeverity": "indeterminate",
            "rawData": null,
            "receiveTime": "2020-01-17T23:23:31.684Z",
            "repeat": true,
            "resource": "web01",
            "service": [
              "Web"
            ],
            "severity": "major",
            "status": "ack",
            "tags": [],
            "text": "Web server web01 is down",
            "timeout": 86400,
            "trendIndication": "moreSevere",
            "type": "exceptionAlert",
            "updateTime": "2020-01-18T02:33:49.536Z",
            "value": null
          },
          "id": "cca2053f-806d-478c-abb3-bbec6fddbb49",
          "status": "ok"
        }
        """

        m.post('/alert', text=send_response)
        result = self.runner.invoke(send, ['-r', 'web01', '-e', 'node_down', '-E', 'Development', '-S', 'Web', '-s', 'major'], obj=self.obj)
        print(result.runner.__dict__)
        self.assertIn('foo', result.output)
        self.assertEqual(result.exit_code, 0)

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
        result = self.runner.invoke(whoami, ['-u'], obj=self.obj)
        self.assertIn('preferred_username  : admin@alerta.io', result.output)
        self.assertEqual(result.exit_code, 0)
