
import click


@click.command('whoami', short_help='Display current logged in user')
@click.pass_obj
def cli(obj):
    """Login using username/password."""
    client = obj['client']
    userinfo = client.userinfo()
    click.echo(userinfo['preferred_username'])
