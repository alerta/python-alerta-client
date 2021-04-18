import sys

import click
from tabulate import tabulate


@click.command('group', short_help='Create user group')
@click.option('--id', '-i', metavar='UUID', help='Group ID')
@click.option('--name', help='Group name')
@click.option('--text', help='Description of user group')
@click.option('--users', '-U', is_flag=True, metavar='ID', help='Get list of group users')
@click.option('--delete', '-D', metavar='ID', help='Delete user group using ID')
@click.pass_obj
def cli(obj, id, name, text, users, delete):
    """Create or delete a user group."""
    client = obj['client']
    if users:
        group_users = client.get_group_users(id)
        timezone = obj['timezone']
        headers = {'id': 'ID', 'name': 'USER', 'email': 'EMAIL', 'roles': 'ROLES', 'status': 'STATUS',
                   'text': 'TEXT', 'createTime': 'CREATED', 'updateTime': 'LAST UPDATED',
                   'lastLogin': 'LAST LOGIN', 'email_verified': 'VERIFIED'}
        click.echo(tabulate([gu.tabular(timezone) for gu in group_users], headers=headers, tablefmt=obj['output']))
    elif delete:
        client.delete_group(delete)
    else:
        try:
            group = client.create_group(name, text)
        except Exception as e:
            click.echo('ERROR: {}'.format(e), err=True)
            sys.exit(1)
        click.echo(group.id)
