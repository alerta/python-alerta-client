import click

from alertaclient.auth.token import Jwt
from alertaclient.auth.utils import get_token


@click.command('token', short_help='Display current auth token')
@click.option('--decode', '-D', is_flag=True, help='Decode auth token.')
@click.pass_obj
def cli(obj, decode):
    """Display the auth token for logged in user, with option to decode it."""
    client = obj['client']
    token = get_token(client.endpoint)
    if decode:
        jwt = Jwt()
        for k, v in jwt.parse(token).items():
            if isinstance(v, list):
                v = ', '.join(v)
            click.echo('{:20}: {}'.format(k, v))
    else:
        click.echo(token)
