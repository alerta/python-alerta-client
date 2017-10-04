
import os

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

default_config = {
    'config_file': '~/.alerta.conf',
    'profile':     None,
    'endpoint':    'http://localhost:8080',
    'key':         '',
    'timezone':    'Europe/London',
    'timeout':     5.0,
    'sslverify':   True,
    'output':      'simple',
    'color':       True,
    'debug':       False
}


class Config(object):

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
