
import configparser
import os

import requests

default_config = {
    'config_file': '~/.alerta.conf',
    'profile': None,
    'endpoint': 'http://localhost:8080',
    'key': '',
    'username': None,
    'password': None,
    'timezone': 'Europe/London',
    'timeout': 5.0,
    'sslverify': True,
    'use_local': [],  # eg. set to ['endpoint'] to prevent server override
    'output': 'simple',
    'color': True,
    'debug': False
}


class Config:

    def __init__(self, config_file):
        self.options = default_config
        self.parser = configparser.RawConfigParser(defaults=self.options)
        config_file = config_file or os.environ.get('ALERTA_CONF_FILE') or self.options['config_file']
        self.parser.read(os.path.expanduser(config_file))

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

    def get_remote_config(self):
        config_url = '{}/config'.format(self.options['endpoint'])
        try:
            r = requests.get(config_url)
            remote_config = r.json()
        except requests.RequestException as e:
            raise

        # remove local exclusions from remote config
        remote_config_only = {k: v for k, v in remote_config.items() if k not in self.options['use_local']}

        # merge local config with remote, giving precedence to remote
        self.options = {**self.options, **remote_config_only}
