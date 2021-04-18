import sys

import click
from tabulate import tabulate


@click.command('group', short_help='Create user group')
@click.option('--id', '-i', metavar='ID', help='Group ID')
@click.option('--name', help='Group name')
@click.option('--text', help='Description of user group')
@click.option('--user', '-U', help='Add user to group')
@click.option('--users', is_flag=True, metavar='ID', help='Get list of group users')
@click.option('--delete', '-D', metavar='ID', help='Delete user group, or remove user from group')
@click.pass_obj
def cli(obj, id, name, text, user, users, delete):
    """
    Create or delete a user group, add and remove users from groups.

    EXAMPLES

        Create a group.

            $ alerta group --name <group-name> --text <description>

        Add a user to a group.

            $ alerta group -id <group-id> --user <user-id>

        List users in a group.

            $ alerta group <group-id> --users

        Delete a user from a group.

            $ alerta group -id <group-id> -D <user-id>

        Delete a group.

            $ alerta group -D <group-id>
    """
    client = obj['client']
    if id and user:
        client.add_user_to_group(id, user)
    elif id and delete:
        client.remove_user_from_group(id, delete)
    elif users:
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
