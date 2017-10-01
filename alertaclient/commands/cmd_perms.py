

import click

from tabulate import tabulate


@click.command('perms', short_help='list role-permission lookups')
@click.pass_obj
@click.pass_context
def cli(ctx, obj):
    """List permissions."""
    client = obj['client']
    timezone = obj['timezone']
    headers = {'id': 'ID', 'scopes': 'SCOPES', 'match': 'ROLE'}
    click.echo(tabulate([p.serialize(timezone) for p in client.get_perms()], headers=headers, tablefmt=ctx.parent.params['output_format']))
