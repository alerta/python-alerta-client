
import click

from alertaclient.auth import clear_token


@click.command('logout', short_help='clear local login credentials')
@click.pass_obj
def cli(obj):
    """Login using username/password."""
    client = obj['client']
    click.echo('logout')
    # save token in .netrc
    clear_token(client.endpoint)
    click.echo('Login credentials removed')
