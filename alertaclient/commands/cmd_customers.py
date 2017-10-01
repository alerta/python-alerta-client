

import click

from tabulate import tabulate


@click.command('customers', short_help='list customer lookups')
@click.pass_obj
@click.pass_context
def cli(obj, client):
    """List customer lookups."""
    client = obj['client']
    timezone = obj['timezone']
    headers = {'id': 'ID', 'customer': 'CUSTOMER', 'match': 'GROUP'}
    click.echo(tabulate([c.serialize(timezone) for c in client.get_customers()], headers=headers, tablefmt=ctx.parent.params['output_format']))
