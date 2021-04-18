import json

import click
from tabulate import tabulate


@click.command('scopes', short_help='List scopes')
@click.pass_obj
def cli(obj):
    """List scopes."""
    client = obj['client']

    if obj['output'] == 'json':
        r = client.http.get('/scopes')
        click.echo(json.dumps(r['scopes'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        headers = {'scope': 'SCOPE'}
        click.echo(tabulate([s.tabular() for s in client.get_scopes()], headers=headers, tablefmt=obj['output']))
