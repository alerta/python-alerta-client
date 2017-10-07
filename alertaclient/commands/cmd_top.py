
import click

from alertaclient.top import Screen


@click.command('top', short_help='Show top offenders and stats')
@click.pass_obj
def cli(obj):
    """Display alerts like unix "top" command."""
    client = obj['client']

    screen = Screen(client)
    screen.run()
