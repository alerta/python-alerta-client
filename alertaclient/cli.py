import os
import sys

import click

from alertaclient.api import Client
from alertaclient.auth import get_token
from alertaclient.config import Config

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='ALERTA',
    default_map={'query': {'compact': True}}
)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          'commands'))


class AlertaCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('alertaclient.commands.cmd_' + name,
                             None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


@click.command(cls=AlertaCLI, context_settings=CONTEXT_SETTINGS)
@click.option('--config-file', metavar='<FILE>', help='Configuration file.')
@click.option('--profile', metavar='<PROFILE>', help='Configuration profile.')
@click.option('--endpoint-url', metavar='<URL>', help='API endpoint URL.')
@click.option('--output', 'output', metavar='<FORMAT>', help='Output format. eg. simple, grid, psql, presto, rst')
@click.option('--color/--no-color', help='Color-coded output based on severity.')
@click.option('--debug', is_flag=True, help='Debug mode.')
@click.pass_context
def cli(ctx, config_file, profile, endpoint_url, output, color, debug):
    """
    Alerta client unified command-line tool.
    """
    config = Config(config_file)
    config.get_config_for_profle(profile)

    ctx.obj = dict()
    ctx.obj['timezone'] = config.options['timezone']
    ctx.obj['output'] = output or config.options['output']
    ctx.obj['color'] = color or config.options['color']

    endpoint = endpoint_url or config.options['endpoint']

    ctx.obj['client'] = Client(
        endpoint=endpoint,
        key=config.options['key'],
        token=get_token(endpoint),
        timeout=float(config.options['timeout']),
        ssl_verify=config.options['sslverify'],
        debug=debug or config.options['debug']
    )
