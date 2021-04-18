import json

import click
from tabulate import tabulate


@click.command('notes', short_help='List notes')
@click.option('--alert-id', '-i', metavar='ID', help='alert IDs (can use short 8-char id)')
@click.pass_obj
def cli(obj, alert_id):
    """List notes."""
    client = obj['client']
    if alert_id:
        if obj['output'] == 'json':
            r = client.http.get('/alert/{}/notes'.format(alert_id))
            click.echo(json.dumps(r['notes'], sort_keys=True, indent=4, ensure_ascii=False))
        else:
            timezone = obj['timezone']
            headers = {
                'id': 'NOTE ID', 'text': 'NOTE', 'user': 'USER', 'type': 'TYPE', 'attributes': 'ATTRIBUTES',
                'createTime': 'CREATED', 'updateTime': 'UPDATED', 'related': 'RELATED ID', 'customer': 'CUSTOMER'
            }
            click.echo(tabulate([n.tabular(timezone) for n in client.get_alert_notes(alert_id)], headers=headers, tablefmt=obj['output']))
    else:
        raise click.UsageError('Need "--alert-id" to list notes.')
