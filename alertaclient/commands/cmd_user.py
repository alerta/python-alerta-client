import sys

import click


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
@click.option('--id', '-i', metavar='UUID', help='User ID')
@click.option('--name', help='Name of user')
@click.option('--email', help='Email address (login username)')
@click.option('--password', help='Password (will prompt if not supplied)')
@click.option('--status', help='Status eg. active, inactive')
@click.option('--role', 'roles', multiple=True, help='List of roles')
@click.option('--text', help='Description of user')
@click.option('--email-verified/--email-not-verified', default=False, help='Email address verified flag')
@click.option('--delete', '-D', metavar='UUID', help='Delete user using ID')
@click.pass_obj
def cli(obj, id, name, email, password, status, roles, text, email_verified, delete):
    """Create user or update user details, including password reset."""
    client = obj['client']
    if delete:
        client.delete_user(delete)
    elif id:
        if not any([name, email, password, status, roles, text, email_verified]):
            click.echo('Nothing to update.')
            sys.exit(1)
        try:
            r = client.update_user(
                id, name=name, email=email, password=password, status=status,
                roles=roles, attributes=None, text=text, email_verified=email_verified
            )
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        if r['status'] == 'ok':
            click.echo('Updated.')
        else:
            click.echo(r['message'])
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
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(user.id)
