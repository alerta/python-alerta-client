import sys

import click


@click.command('user', short_help='Update user')
@click.option('--id', '-i', metavar='UUID', help='User ID')
@click.option('--name')
@click.option('--email')
@click.option('--password')
@click.option('--status')
@click.option('--role', 'roles', multiple=True)
@click.option('--text')
@click.option('--email-verified/--email-not-verified', default=None)
@click.option('--delete', '-D', metavar='UUID', help='delete user')
@click.pass_obj
def cli(obj, id, name, email, password, status, roles, text, email_verified, delete):
    """Update user details, including password reset."""
    client = obj['client']
    if delete:
        if name or email or password or status or roles or text or email_verified:
            raise click.UsageError('Option "--delete" is mutually exclusive.')
        client.delete_user(delete)
    else:
        try:
            r = client.update_user(
                id, name=name, email=email, password=password, status=status,
                roles=roles, text=text, email_verified=email_verified
            )
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        if r['status'] == 'ok':
            click.echo('Updated.')
        else:
            click.echo(r['message'])
