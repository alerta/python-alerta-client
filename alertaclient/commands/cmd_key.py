import sys
from datetime import datetime, timedelta

import click


@click.command('key', short_help='Create API key')
@click.option('--api-key', '-K', help='User-defined API Key.  [default: random string]')
@click.option('--username', '-u', help='User (Admin only)')
@click.option('--scope', 'scopes', multiple=True, help='List of permissions eg. admin:keys, write:alerts')
@click.option('--duration', metavar='SECONDS', type=int, help='Duration API key is valid')
@click.option('--text', help='Description of API key use')
@click.option('--customer', metavar='STRING', help='Customer')
@click.option('--delete', '-D', metavar='ID', help='Delete API key using ID or KEY')
@click.pass_obj
def cli(obj, api_key, username, scopes, duration, text, customer, delete):
    """Create or delete an API key."""
    client = obj['client']
    if delete:
        client.delete_key(delete)
    else:
        try:
            expires = datetime.utcnow() + timedelta(seconds=duration) if duration else None
            key = client.create_key(username, scopes, expires, text, customer, key=api_key)
        except Exception as e:
            click.echo(f'ERROR: {e}', err=True)
            sys.exit(1)
        click.echo(key.key)
