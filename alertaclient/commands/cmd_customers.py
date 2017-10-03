

import click

from tabulate import tabulate


@click.command('customers', short_help='List customer lookups')
@click.pass_obj
@click.pass_context
def cli(ctx, obj):
    """List customer lookups."""
    client = obj['client']
    headers = {'id': 'ID', 'customer': 'CUSTOMER', 'match': 'GROUP'}
    click.echo(tabulate([c.serialize() for c in client.get_customers()], headers=headers, tablefmt=ctx.parent.params['output_format']))
