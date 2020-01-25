import unittest
from uuid import UUID

import requests_mock
from click.testing import CliRunner

from alertaclient.api import Client
from alertaclient.commands.cmd_heartbeat import cli as heartbeat_cmd
from alertaclient.commands.cmd_whoami import cli as whoami_cmd
from alertaclient.config import Config


class CommandsTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        config = Config(config_file=None)
        self.obj = config.options
        self.obj['client'] = self.client

        self.runner = CliRunner(echo_stdin=True)

    @requests_mock.mock()
    def test_send_cmd(self, m):

        config_response = """
        {}
        """
        m.get('/config', text=config_response)

        send_response = """
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

        m.post('/heartbeat', text=send_response)
        result = self.runner.invoke(heartbeat_cmd, ['-E', 'Production', '-S', 'Web', '-s', 'major'], obj=self.obj)
        UUID(result.output.strip())
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
        result = self.runner.invoke(whoami_cmd, ['-u'], obj=self.obj)
        self.assertIn('preferred_username  : admin@alerta.io', result.output)
        self.assertEqual(result.exit_code, 0)
