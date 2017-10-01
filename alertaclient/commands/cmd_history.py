
import click
from tabulate import tabulate

from alertaclient.utils import build_query


@click.command('history', short_help='show alert history')
@click.option('--ids', '-i', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--compact', is_flag=True, help='show alert details')
@click.pass_obj
@click.pass_context
def cli(ctx, obj, ids, filters, compact):
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
        tabulate([a.serialize(timezone) for a in alerts], headers=headers, tablefmt=ctx.parent.params['output_format']))
