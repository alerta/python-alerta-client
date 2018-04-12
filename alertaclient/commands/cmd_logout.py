
import click

from alertaclient.auth.utils import clear_token


@click.command('logout', short_help='Clear login credentials')
@click.pass_obj
def cli(obj):
    """Clear local login credentials from netrc file."""
    client = obj['client']
    clear_token(client.endpoint)
    click.echo('Login credentials removed')
