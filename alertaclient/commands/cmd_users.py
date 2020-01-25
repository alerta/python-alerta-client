import json

import click
from tabulate import tabulate


@click.command('users', short_help='List users')
@click.option('--role', 'roles', multiple=True, help='Filter users by role')
@click.pass_obj
def cli(obj, roles):
    """List users."""
    client = obj['client']
    query = [('roles', r) for r in roles]

    if obj['output'] == 'json':
        r = client.http.get('/users', query)
        click.echo(json.dumps(r['users'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        timezone = obj['timezone']
        headers = {'id': 'ID', 'name': 'USER', 'email': 'EMAIL', 'roles': 'ROLES', 'status': 'STATUS', 'text': 'TEXT',
                   'createTime': 'CREATED', 'updateTime': 'LAST UPDATED', 'lastLogin': 'LAST LOGIN', 'email_verified': 'VERIFIED'}
        click.echo(
            tabulate([u.tabular(timezone) for u in client.get_users(query)], headers=headers, tablefmt=obj['output'])
        )
