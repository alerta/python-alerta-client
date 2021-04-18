import click

from alertaclient.utils import build_query


@click.command('update', short_help='Update alert attributes')
@click.option('--ids', '-i', metavar='ID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--query', '-q', 'query', metavar='QUERY', help='severity:"warning" AND resource:web')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--attributes', '-A', metavar='KEY=VALUE', multiple=True, required=True, help='List of attributes eg. priority=high')
@click.pass_obj
def cli(obj, ids, query, filters, attributes):
    """Update alert attributes."""
    client = obj['client']
    if ids:
        total = len(ids)
    else:
        if query:
            query = [('q', query)]
        else:
            query = build_query(filters)
        total, _, _ = client.get_count(query)
        ids = [a.id for a in client.get_alerts(query)]

    with click.progressbar(ids, label='Updating {} alerts'.format(total)) as bar:
        for id in bar:
            client.update_attributes(id, dict(a.split('=') for a in attributes))
