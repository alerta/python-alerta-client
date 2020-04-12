import sys

import click

from alertaclient.exceptions import AuthError


@click.command('signup', short_help='Sign-up new user')
@click.option('--name', help='Name of user')
@click.option('--email', help='Email address (login username)')
@click.option('--password', help='Password')
@click.option('--status', help='Status eg. active, inactive')
@click.option('--text', help='Description of user')
@click.pass_obj
def cli(obj, name, email, password, status, text):
    """Create new Basic Auth user."""
    client = obj['client']
    if not email:
        raise click.UsageError('Need "--email" to sign-up new user.')
    if not password:
        raise click.UsageError('Need "--password" to sign-up new user.')
    try:
        r = client.signup(name=name, email=email, password=password, status=status, attributes=None, text=text)
    except Exception as e:
        click.echo('ERROR: {}'.format(e), err=True)
        sys.exit(1)
    if 'token' in r:
        click.echo('Signed Up.')
    else:
        raise AuthError
