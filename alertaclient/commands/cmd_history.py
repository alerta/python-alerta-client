
import click
from tabulate import tabulate

from alertaclient.utils import build_query


@click.command('history', short_help='Show alert history')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.pass_obj
def cli(obj, ids, filters):
    """Show status and severity changes for alerts."""
    client = obj['client']
    timezone = obj['timezone']
    if ids:
        query = [('id', x) for x in ids]
    else:
        query = build_query(filters)
    alerts = client.get_history(query)

    headers = {'id': 'ID', 'updateTime': 'LAST UPDATED', 'severity': 'SEVERITY', 'status': 'STATUS',
               'type': 'TYPE', 'customer': 'CUSTOMER', 'environment': 'ENVIRONMENT', 'service': 'SERVICE',
               'resource': 'RESOURCE', 'group': 'GROUP', 'event': 'EVENT', 'value': 'VALUE', 'text': 'TEXT'}
    click.echo(
        tabulate([a.tabular(timezone) for a in alerts], headers=headers, tablefmt=obj['output']))
