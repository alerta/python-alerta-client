

import click

from tabulate import tabulate


@click.command('users', short_help='List users')
@click.pass_obj
def cli(obj):
    """List users."""
    client = obj['client']
    timezone = obj['timezone']
    headers = {'id': 'ID', 'name': 'USER', 'email': 'EMAIL', 'roles': 'ROLES', 'status': 'STATUS', 'text': 'TEXT',
               'createTime': 'CREATED', 'updateTime': 'LAST UPDATED', 'lastLogin': 'LAST LOGIN', 'email_verified': 'VERIFIED'}
    click.echo(tabulate([u.tabular(timezone) for u in client.get_users()], headers=headers, tablefmt=obj['output']))
