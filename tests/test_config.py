import contextlib
import os
import unittest

from alertaclient.api import Client
from alertaclient.config import Config


@contextlib.contextmanager
def mod_env(*remove, **update):
    """
    See https://stackoverflow.com/questions/2059482#34333710

    Temporarily updates the ``os.environ`` dictionary in-place.

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]


class CommandsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_env_vars(self):

        config = Config(config_file=None)
        self.assertEqual(config.options['config_file'], '~/.alerta.conf')

        with mod_env(
                ALERTA_CONF_FILE='~/.alerta.test.conf',
                ALERTA_DEFAULT_PROFILE='test-profile',
                ALERTA_ENDPOINT='http://foo/bar/baz',
                ALERTA_API_KEY='test-key',
                REQUESTS_CA_BUNDLE='',
                CLICOLOR='',
                DEBUG='1'
        ):

            # conf file
            config = Config(config_file=None)
            self.assertEqual(config.options['config_file'], '~/.alerta.test.conf', os.environ)
            config = Config(config_file='/dev/null')
            self.assertEqual(config.options['config_file'], '/dev/null')

            # profile
            config = Config(config_file=None)
            config.get_config_for_profle()
            self.assertEqual(config.options['profile'], 'test-profile', os.environ)

            # endpoint
            self.client = Client()
            self.assertEqual(self.client.endpoint, 'http://foo/bar/baz')

            # api key
            self.assertEqual(config.options['key'], 'test-key')
