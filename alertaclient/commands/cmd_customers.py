

import click

from tabulate import tabulate


@click.command('customers', short_help='List customer lookups')
@click.pass_obj
def cli(obj):
    """List customer lookups."""
    client = obj['client']
    headers = {'id': 'ID', 'customer': 'CUSTOMER', 'match': 'GROUP'}
    click.echo(tabulate([c.tabular() for c in client.get_customers()], headers=headers, tablefmt=obj['output']))
