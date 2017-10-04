
import click
from tabulate import tabulate

from alertaclient.utils import build_query


@click.command('raw', short_help='Show alert raw data')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.pass_obj
def cli(obj, ids, filters):
    client = obj['client']
    """Show raw data for alerts."""
    if ids:
        query = [('id', x) for x in ids]
    else:
        query = build_query(filters)
    alerts = client.search(query)

    headers = {'id': 'ID', 'rawData': 'RAW DATA'}
    click.echo(
        tabulate([{'id': a.id, 'rawData': a.raw_data} for a in alerts], headers=headers, tablefmt=obj['output']))
