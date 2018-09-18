
import sys

import click

from alertaclient.auth import github, gitlab, google
from alertaclient.auth.token import Jwt
from alertaclient.auth.utils import save_token
from alertaclient.exceptions import AuthError


@click.command('login', short_help='Login with user credentials')
@click.argument('username', required=False)
@click.pass_obj
def cli(obj, username):
    """Authenticate using Github, Gitlab, Google OAuth2 or Basic Auth
    username/password instead of using an API key."""
    client = obj['client']
    provider = obj['provider']
    client_id = obj['client_id']

    try:
        if provider == 'github':
            token = github.login(client, obj['github_url'], client_id)['token']
        elif provider == 'gitlab':
            token = gitlab.login(client, obj['gitlab_url'], client_id)['token']
        elif provider == 'google':
            if not username:
                username = click.prompt('Email')
            token = google.login(client, username, client_id)['token']
        elif provider == 'basic':
            if not username:
                username = click.prompt('Email')
            password = click.prompt('Password', hide_input=True)
            token = client.login(username, password)['token']
        else:
            click.echo('ERROR: unknown provider {provider}'.format(provider=provider))
            sys.exit(1)
    except Exception as e:
        raise AuthError(e)

    jwt = Jwt()
    preferred_username = jwt.parse(token)['preferred_username']
    if preferred_username:
        save_token(client.endpoint, preferred_username, token)
        click.echo('Logged in as {}'.format(preferred_username))
    else:
        click.echo('Failed to login.')
        sys.exit(1)
