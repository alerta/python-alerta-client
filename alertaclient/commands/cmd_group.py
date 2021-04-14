import sys

import click
from tabulate import tabulate


@click.command('group', short_help='Create user group and assign user to group')
@click.option('--name', help='Group name ')
@click.option('--text', help='Description of user group')
@click.option('--id', metavar='UUID', help='Group ID')
@click.option('--listusers', '-L', metavar='GROUPNAME', help='Lists users of group using Name')
@click.option('--listusersid', '-l', metavar='GROUPID', help='Lists users of group using ID')
@click.option('--delete', '-D', metavar='ID', help='Delete user group using ID')
@click.option('--assignid', '-A', metavar='USERID', help='Assign user to group using ID')
@click.option('--assignname', '-a', metavar='USERNAME', help='Assign user to group using name')
@click.option('--removeid', '-R', metavar='USERID', help='Remove user from group using ID')
@click.option('--removename', '-r', metavar='USERNAME', help='Remove user from group using name')
@click.pass_obj
def cli(obj, name, text, id, delete, assignid, assignname, removeid, removename, listusers, listusersid):
    """Create or delete a user group."""
    client = obj['client']

    """List users in group by id"""
    if listusersid:
        headers = {'id': 'ID', 'name': 'NAME', 'status': 'STATUS', 'email': 'EMAIL', 'roles': 'ROLES'}
        click.echo(tabulate([grp_tabular(g) for g in client.get_group_users(listusersid)], headers=headers, tablefmt=obj['output']))

    elif listusers:
        """List users in group by name"""
        group = [x for x in client.get_users_groups() if x.name == listusers]
        if len(group) > 0:
            groupid = group[0].id
        else:
            click.echo('ERROR: Group {} not found'.format(listusers), err=True)
            sys.exit(1)
        headers = {'id': 'ID', 'name': 'NAME', 'status': 'STATUS', 'email': 'EMAIL', 'roles': 'ROLES'}
        click.echo(tabulate([grp_tabular(g) for g in client.get_group_users(groupid)], headers=headers, tablefmt=obj['output']))
        sys.exit(0)
    elif assignname and name:
        """Add user to group by name"""
        user = [x for x in client.get_users() if x.name == assignname]
        if len(user) > 0:
            userid = user[0].id
        else:
            click.echo('ERROR: User {} not found'.format(assignname), err=True)
            sys.exit(1)
        group = [x for x in client.get_users_groups() if x.name == name]
        if len(group) > 0:
            groupid = group[0].id
        else:
            click.echo('ERROR: Group {} not found'.format(name), err=True)
            sys.exit(1)
        client.add_user_to_group(groupid, userid)
        sys.exit(0)
    elif removename and name:
        """Remove user to group by name."""
        user = [x for x in client.get_users() if x.name == removename]
        if len(user) > 0:
            userid = user[0].id
        else:
            click.echo('ERROR: User {} not found'.format(removename), err=True)
            sys.exit(1)
        group = [x for x in client.get_users_groups() if x.name == name]
        if len(group) > 0:
            groupid = group[0].id
        else:
            click.echo('ERROR: Group {} not found'.format(name), err=True)
            sys.exit(1)
        client.remove_user_from_group(groupid, userid)
        sys.exit(0)
    elif assignid and id:
        """Add user to group by ID."""
        client.add_user_to_group(id, assignid)
        sys.exit(0)
    elif removeid and id:
        """Remove user to group by ID."""
        client.remove_user_from_group(id, removeid)
        sys.exit(0)
    elif delete:
        client.delete_group(delete)
    else:
        try:
            group = client.create_group(name, text)
        except Exception as e:
            click.echo('ERROR: {}'.format(e), err=True)
            sys.exit(1)
        click.echo(group.id)


def grp_tabular(user):
    """Table for users from group"""
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'status': user.status,
        'roles': ','.join(user.roles)
    }
