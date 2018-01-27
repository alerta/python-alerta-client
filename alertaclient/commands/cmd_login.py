
import click

from alertaclient.auth import save_token
from alertaclient.exceptions import AuthError


@click.command('login', short_help='Login with user credentials')
@click.option('--username', metavar='EMAIL', prompt='Email')
@click.password_option(confirmation_prompt=False)
@click.pass_obj
def cli(obj, username, password):
    """Use this tool with username/password instead of API key."""
    client = obj['client']
    r = client.login(username, password)
    if 'token' in r:
        token = r['token']
    else:
        raise AuthError
    save_token(client.endpoint, username, token)
    click.echo('Logged in as {}'.format(username))
