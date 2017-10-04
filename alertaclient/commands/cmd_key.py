import sys
from datetime import datetime, timedelta

import click


@click.command('key', short_help='Create API key')
@click.option('--username', '-u')
@click.option('--scope', 'scopes', multiple=True, help='List of permissions eg. admin:keys, write:alerts')
@click.option('--duration', type=int)
@click.option('--text')
@click.option('--delete', '-D', metavar='ID', help='Delete API key')
@click.pass_obj
def cli(obj, username, scopes, duration, text, delete):
    """Create or delete an API key."""
    client = obj['client']
    if delete:
        if username or scopes or duration or text:
            raise click.UsageError('Option "--delete" is mutually exclusive.')
        client.delete_key(delete)
    else:
        try:
            expires = datetime.utcnow() + timedelta(seconds=duration) if duration else None
            key = client.create_key(username, scopes, expires, text)
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(key.key)
