import configparser
import json
import os

import requests

from alertaclient.exceptions import ClientException

default_config = {
    'config_file': '~/.alerta.conf',
    'profile': None,
    'endpoint': 'http://localhost:8080',
    'key': '',
    'secret': None,
    'client_id': None,
    'username': None,
    'password': None,
    'timezone': 'Europe/London',
    'timeout': 5.0,
    'sslverify': True,
    'sslcert': None,
    'sslkey': None,
    'output': 'simple',
    'color': True,
    'debug': False
}


class Config:

    def __init__(self, config_file, config_override=None):
        self.options = default_config
        self.parser = configparser.RawConfigParser(defaults=self.options)

        self.options['config_file'] = config_file or os.environ.get('ALERTA_CONF_FILE') or self.options['config_file']
        self.parser.read(os.path.expanduser(self.options['config_file']))

        self.options.update(config_override or {})

    def get_config_for_profle(self, profile=None):
        want_profile = profile or os.environ.get('ALERTA_DEFAULT_PROFILE') or self.parser.defaults().get('profile')

        if want_profile and self.parser.has_section('profile %s' % want_profile):
            for opt in self.options:
                try:
                    self.options[opt] = self.parser.getboolean('profile %s' % want_profile, opt)
                except (ValueError, AttributeError):
                    self.options[opt] = self.parser.get('profile %s' % want_profile, opt)
        else:
            for opt in self.options:
                try:
                    self.options[opt] = self.parser.getboolean('DEFAULT', opt)
                except (ValueError, AttributeError):
                    self.options[opt] = self.parser.get('DEFAULT', opt)

        self.options['profile'] = want_profile
        self.options['endpoint'] = os.environ.get('ALERTA_ENDPOINT', self.options['endpoint'])
        self.options['key'] = os.environ.get('ALERTA_API_KEY', self.options['key'])

    def get_remote_config(self, endpoint=None):
        config_url = '{}/config'.format(endpoint or self.options['endpoint'])
        try:
            r = requests.get(config_url, verify=self.options['sslverify'], cert=(self.options['sslcert'], self.options['sslkey']))
            r.raise_for_status()
            remote_config = r.json()
        except requests.RequestException as e:
            raise ClientException('Failed to get config from {}. Reason: {}'.format(config_url, e))
        except json.decoder.JSONDecodeError:
            raise ClientException('Failed to get config from {}: Reason: not a JSON object'.format(config_url))

        self.options = {**remote_config, **self.options}
