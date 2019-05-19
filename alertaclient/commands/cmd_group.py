import sys

import click


@click.command('group', short_help='Create user group')
@click.option('--name', help='Group name')
@click.option('--text', help='Description of user group')
@click.option('--delete', '-D', metavar='ID', help='Delete user group using ID')
@click.pass_obj
def cli(obj, name, text, delete):
    """Create or delete a user group."""
    client = obj['client']
    if delete:
        client.delete_group(delete)
    else:
        try:
            group = client.create_group(name, text)
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(group.id)
