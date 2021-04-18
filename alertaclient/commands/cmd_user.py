import sys

import click
from tabulate import tabulate


class CommandWithOptionalPassword(click.Command):

    def parse_args(self, ctx, args):
        for i, a in enumerate(args):
            if args[i] == '--password':
                try:
                    password = args[i + 1] if not args[i + 1].startswith('--') else None
                except IndexError:
                    password = None
                if not password:
                    password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
                    args.insert(i + 1, password)
        return super().parse_args(ctx, args)


@click.command('user', cls=CommandWithOptionalPassword, short_help='Update user')
@click.option('--id', '-i', metavar='ID', help='User ID')
@click.option('--name', help='Name of user')
@click.option('--email', help='Email address (login username)')
@click.option('--password', help='Password (will prompt if not supplied)')
@click.option('--status', help='Status eg. active, inactive')
@click.option('--role', 'roles', multiple=True, help='List of roles')
@click.option('--text', help='Description of user')
@click.option('--email-verified/--email-not-verified', default=None, help='Email address verified flag')
@click.option('--groups', is_flag=True, help='Get list of user groups')
@click.option('--delete', '-D', metavar='ID', help='Delete user using ID')
@click.pass_obj
def cli(obj, id, name, email, password, status, roles, text, email_verified, groups, delete):
    """Create user, show or update user details, including password reset, list user groups and delete user."""
    client = obj['client']
    if groups:
        user_groups = client.get_user_groups(id)
        headers = {'id': 'ID', 'name': 'USER', 'text': 'TEXT', 'count': 'COUNT'}
        click.echo(tabulate([ug.tabular() for ug in user_groups], headers=headers, tablefmt=obj['output']))
    elif delete:
        client.delete_user(delete)
    elif id:
        if not any([name, email, password, status, roles, text, (email_verified is not None)]):
            user = client.get_user(id)
            timezone = obj['timezone']
            headers = {'id': 'ID', 'name': 'USER', 'email': 'EMAIL', 'roles': 'ROLES', 'status': 'STATUS',
                       'text': 'TEXT',
                       'createTime': 'CREATED', 'updateTime': 'LAST UPDATED', 'lastLogin': 'LAST LOGIN',
                       'email_verified': 'VERIFIED'}
            click.echo(tabulate([user.tabular(timezone)], headers=headers, tablefmt=obj['output']))
        else:
            try:
                user = client.update_user(
                    id, name=name, email=email, password=password, status=status,
                    roles=roles, attributes=None, text=text, email_verified=email_verified
                )
            except Exception as e:
                click.echo('ERROR: {}'.format(e), err=True)
                sys.exit(1)
            click.echo(user.id)
    else:
        if not email:
            raise click.UsageError('Need "--email" to create user.')
        if not password:
            password = click.prompt('Password', hide_input=True)
        try:
            user = client.create_user(
                name=name, email=email, password=password, status=status,
                roles=roles, attributes=None, text=text, email_verified=email_verified
            )
        except Exception as e:
            click.echo('ERROR: {}'.format(e), err=True)
            sys.exit(1)
        click.echo(user.id)
