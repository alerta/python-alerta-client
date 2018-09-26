import click

from alertaclient.utils import build_query


@click.command('delete', short_help='Delete alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.pass_obj
def cli(obj, ids, filters):
    """Delete alerts."""
    client = obj['client']
    label = 'Deleting'
    if ids:
        total = len(ids)
        with click.progressbar(ids, label='{} {} alerts'.format(label, total)) as bar:
            for id in bar:
                client.delete_alert(id)
    else:
        if not filters:
            click.confirm('Deleting all alerts. Do you want to continue?', abort=True)
        query = build_query(filters)
        r = client.bulk_delete(query)
        ids = r['deleted']
        total = r['count']
        with click.progressbar(ids, label='{} {} alerts'.format(label, total)) as bar:
            for id in bar:
                pass
