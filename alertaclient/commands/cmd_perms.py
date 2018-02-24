
import json

import click
from tabulate import tabulate


@click.command('perms', short_help='List role-permission lookups')
@click.pass_obj
def cli(obj):
    """List permissions."""
    client = obj['client']

    if obj['output'] == 'json':
        r = client.http.get('/perms')
        click.echo(json.dumps(r['permissions'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        headers = {'id': 'ID', 'scopes': 'SCOPES', 'match': 'ROLE'}
        click.echo(tabulate([p.tabular() for p in client.get_perms()], headers=headers, tablefmt=obj['output']))
