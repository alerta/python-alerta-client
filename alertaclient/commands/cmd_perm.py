import sys

import click


@click.command('perm', short_help='Add role-permission lookup')
@click.option('--role', help='Role name')
@click.option('--scope', 'scopes', multiple=True, help='List of permissions eg. admin:keys, write:alerts')
@click.option('--delete', '-D', metavar='ID', help='Delete role using ID')
@click.pass_obj
def cli(obj, role, scopes, delete):
    """Add or delete role-to-permission lookup entry."""
    client = obj['client']
    if delete:
        client.delete_perm(delete)
    else:
        if not role:
            raise click.UsageError('Missing option "--role".')
        if not scopes:
            raise click.UsageError('Missing option "--scope".')
        try:
            perm = client.create_perm(role, scopes)
        except Exception as e:
            click.echo('ERROR: {}'.format(e), err=True)
            sys.exit(1)
        click.echo(perm.id)
