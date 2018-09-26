import click

from alertaclient.utils import build_query


@click.command('tag', short_help='Tag alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--tag', '-T', 'tags', required=True, multiple=True, help='List of tags')
@click.pass_obj
def cli(obj, ids, filters, tags):
    """Add tags to alerts."""
    client = obj['client']
    label = 'Tagging'
    if ids:
        total = len(ids)
        with click.progressbar(ids, label='{} {} alerts'.format(label, total)) as bar:
            for id in bar:
                client.tag_alert(id, tags)
    else:
        query = build_query(filters)
        r = client.bulk_tag(query, tags)
        ids = r['updated']
        total = r['count']
        with click.progressbar(ids, label='{} {} alerts'.format(label, total)) as bar:
            for id in bar:
                pass
