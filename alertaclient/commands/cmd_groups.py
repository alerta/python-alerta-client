
import json

import click
from tabulate import tabulate


@click.command('groups', short_help='List user groups')
@click.pass_obj
def cli(obj):
    """List groups."""
    client = obj['client']

    if obj['output'] == 'json':
        r = client.http.get('/groups')
        click.echo(json.dumps(r['groups'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        headers = {'id': 'ID', 'name': 'NAME', 'count': 'USERS', 'text': 'DESCRIPTION'}
        click.echo(tabulate([g.tabular() for g in client.get_users_groups()], headers=headers, tablefmt=obj['output']))
