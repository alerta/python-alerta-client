import json

import click
from tabulate import tabulate


@click.command('blackouts', short_help='List alert suppressions')
@click.option('--purge', is_flag=True, help='Delete all expired blackouts')
@click.pass_obj
def cli(obj, purge):
    """List alert suppressions."""
    client = obj['client']

    if obj['output'] == 'json':
        r = client.http.get('/blackouts')
        click.echo(json.dumps(r['blackouts'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        timezone = obj['timezone']
        headers = {
            'id': 'ID', 'priority': 'P', 'environment': 'ENVIRONMENT', 'service': 'SERVICE', 'resource': 'RESOURCE',
            'event': 'EVENT', 'group': 'GROUP', 'tags': 'TAGS', 'origin': 'ORIGIN', 'customer': 'CUSTOMER',
            'startTime': 'START', 'endTime': 'END', 'duration': 'DURATION', 'user': 'USER',
            'createTime': 'CREATED', 'text': 'COMMENT', 'status': 'STATUS', 'remaining': 'REMAINING'
        }
        blackouts = client.get_blackouts()
        click.echo(tabulate([b.tabular(timezone) for b in blackouts], headers=headers, tablefmt=obj['output']))

        expired = [b for b in blackouts if b.status == 'expired']
        if purge:
            with click.progressbar(expired, label='Purging {} blackouts'.format(len(expired))) as bar:
                for b in bar:
                    client.delete_blackout(b.id)
