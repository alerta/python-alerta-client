import click

from alertaclient.utils import build_query


@click.command('update', short_help='Update alert attributes')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--attributes', '-A', metavar='KEY=VALUE', multiple=True, required=True, help='List of attributes eg. priority=high')
@click.pass_obj
def cli(obj, ids, filters, attributes):
    """Update alert attributes."""
    client = obj['client']
    label = 'Updating'
    if ids:
        total = len(ids)
        with click.progressbar(ids, label='{} {} alerts'.format(label, total)) as bar:
            for id in bar:
                client.update_attributes(id, dict(a.split('=') for a in attributes))
    else:
        query = build_query(filters)
        r = client.bulk_update_attributes(query, dict(a.split('=') for a in attributes))
        ids = r['updated']
        total = r['count']
        with click.progressbar(ids, label='{} {} alerts'.format(label, total)) as bar:
            for id in bar:
                pass
