import json

import click
from tabulate import tabulate


@click.command('perms', short_help='List role-permission lookups')
@click.option('--scope', 'scopes', multiple=True, help='Filter roles by scope eg. admin:keys, write:alerts')
@click.pass_obj
def cli(obj, scopes):
    """List permissions."""
    client = obj['client']
    query = [('scopes', s) for s in scopes]

    if obj['output'] == 'json':
        r = client.http.get('/perms', query)
        click.echo(json.dumps(r['permissions'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        headers = {'id': 'ID', 'scopes': 'SCOPES', 'match': 'ROLE'}
        click.echo(tabulate([p.tabular() for p in client.get_perms(query)], headers=headers, tablefmt=obj['output']))
