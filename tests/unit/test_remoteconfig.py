import unittest

import requests
import requests_mock
from requests_mock import Adapter

from alertaclient.cli import Config
from alertaclient.exceptions import ClientException


class RemoteConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.adapter = Adapter()
        self.config = Config('')
        self.remote_json_config = """
          {
            "actions": [],
            "alarm_model": {
              "name": "Alerta 8.0.1"
            },
            "audio": {
              "new": null
            },
            "auth_required": false,
            "azure_tenant": null,
            "client_id": null,
            "colors": {
              "highlight": "skyblue ",
              "severity": {
                "cleared": "#00CC00",
                "critical": "red",
                "debug": "#9D006D",
                "indeterminate": "lightblue",
                "informational": "#00CC00",
                "major": "orange",
                "minor": "yellow",
                "normal": "#00CC00",
                "ok": "#00CC00",
                "security": "blue",
                "trace": "#7554BF",
                "unknown": "silver",
                "warning": "dodgerblue"
              },
              "text": "black"
            },
            "columns": ["severity", "status", "lastReceiveTime",
                        "duplicateCount",
                        "customer", "environment", "service", "resource",
                        "event", "value", "text"],
            "customer_views": false,
            "dates": {
              "longDate": "d/M/yyyy h:mm:ss.sss a",
              "mediumDate": "EEE d MMM HH:mm",
              "shortTime": "HH:mm"
            },
            "email_verification": false,
            "endpoint": "http://localhost:8080/api",
            "github_url": "https://github.com",
            "gitlab_url": "https://gitlab.com",
            "keycloak_realm": null,
            "keycloak_url": null,
            "pingfederate_url": null,
            "provider": "basic",
            "refresh_interval": 5000,
            "severity": {
              "cleared": 5,
              "critical": 1,
              "debug": 7,
              "indeterminate": 5,
              "informational": 6,
              "major": 2,
              "minor": 3,
              "normal": 5,
              "ok": 5,
              "security": 0,
              "trace": 8,
              "unknown": 9,
              "warning": 4
            },
            "signup_enabled": true,
            "site_logo_url": "",
            "sort_by": "lastReceiveTime",
            "tracking_id": null
          }
          """

    @requests_mock.mock()
    def test_config_success(self, m):
        """Tests successful remote config fetch"""
        m.get('/api/config', text=self.remote_json_config, status_code=200)
        self.config.get_remote_config('http://localhost:8080/api')
        self.assertEqual(self.config.options['alarm_model']['name'], 'Alerta 8.0.1')

    @requests_mock.mock()
    def test_config_timeout(self, m):
        m.get('/api/config', exc=requests.exceptions.ConnectTimeout)
        with self.assertRaises(ClientException):
            self.config.get_remote_config('http://localhost:8080/api')

    @requests_mock.mock()
    def test_config_not_found(self, m):

        m.get('/config', status_code=404)
        with self.assertRaises(ClientException):
            self.config.get_remote_config('http://localhost:8080')

    @requests_mock.mock()
    def test_config_not_json(self, m):
        """Tests that URL is accessible (HTTP 200)
        but there is no Alerta API config in JSON"""

        m.get('/sometext/config', text='Some random text', status_code=200)
        with self.assertRaises(ClientException):
            self.config.get_remote_config('http://localhost:8080/sometext')
