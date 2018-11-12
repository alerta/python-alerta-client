import unittest

import requests_mock
from click.testing import CliRunner

from alertaclient.api import Client
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
