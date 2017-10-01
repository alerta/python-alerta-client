
import click

from alertaclient.auth import save_token


@click.command('login', short_help='login with user credentials')
@click.option('--username', prompt='Email')
@click.password_option(confirmation_prompt=False)
@click.pass_obj
def cli(obj, username, password):
    """Login using username/password."""
    client = obj['client']
    token = client.login(username, password)
    # save token in .netrc
    save_token(client.endpoint, username, token)
    click.echo('Logged in as {}'.format(username))
