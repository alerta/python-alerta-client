

import click

from tabulate import tabulate


@click.command('perms', short_help='List role-permission lookups')
@click.pass_obj
def cli(obj):
    """List permissions."""
    client = obj['client']
    headers = {'id': 'ID', 'scopes': 'SCOPES', 'match': 'ROLE'}
    click.echo(tabulate([p.tabular() for p in client.get_perms()], headers=headers, tablefmt=obj['output']))
