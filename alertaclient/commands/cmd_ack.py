import click

from alertaclient.utils import build_query


@click.command('ack', short_help='Acknowledge alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--text', help='Message associated with status change')
@click.pass_obj
def cli(obj, ids, filters, text):
    """Set alert status to 'ack'."""
    client = obj['client']
    action = 'ack'
    label = 'Acking'
    if ids:
        total = len(ids)
        with click.progressbar(ids, label='{} {} alerts'.format(label, total)) as bar:
            for id in bar:
                client.action(id, action=action, text=text or 'status changed using CLI')
    else:
        query = build_query(filters)
        r = client.bulk_action(query, action=action, text=text or 'bulk status changed using CLI')
        ids = r['updated']
        total = r['count']
        with click.progressbar(ids, label='{} {} alerts'.format(label, total)) as bar:
            for id in bar:
                pass
