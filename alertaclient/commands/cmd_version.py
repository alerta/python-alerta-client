
import click
from requests import __version__ as requests_version

from alertaclient.version import __version__ as client_version


@click.command('version', short_help='Display version info')
@click.pass_obj
@click.pass_context
def cli(ctx, obj):
    """Show Alerta server and client versions."""
    client = obj['client']
    click.echo('alerta {}'.format(client.mgmt_status()['version']))
    click.echo('alerta client {}'.format(client_version))
    click.echo('requests {}'.format(requests_version))
    click.echo('click {}'.format(click.__version__))
    ctx.exit()
