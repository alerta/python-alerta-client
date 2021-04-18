import json

import click
from tabulate import tabulate

from alertaclient.utils import build_query


@click.command('history', short_help='Show alert history')
@click.option('--ids', '-i', metavar='ID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--query', '-q', 'query', metavar='QUERY', help='severity:"warning" AND resource:web')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.pass_obj
def cli(obj, ids, query, filters):
    """Show status and severity changes for alerts."""
    client = obj['client']

    if obj['output'] == 'json':
        r = client.http.get('/alerts/history')
        click.echo(json.dumps(r['history'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        timezone = obj['timezone']
        if ids:
            query = [('id', x) for x in ids]
        elif query:
            query = [('q', query)]
        else:
            query = build_query(filters)
        alerts = client.get_history(query)

        headers = {'id': 'ID', 'updateTime': 'LAST UPDATED', 'severity': 'SEVERITY', 'status': 'STATUS',
                   'type': 'TYPE', 'customer': 'CUSTOMER', 'environment': 'ENVIRONMENT', 'service': 'SERVICE',
                   'resource': 'RESOURCE', 'group': 'GROUP', 'event': 'EVENT', 'value': 'VALUE', 'text': 'TEXT'}
        click.echo(
            tabulate([a.tabular(timezone) for a in alerts], headers=headers, tablefmt=obj['output']))
