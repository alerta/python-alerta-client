import click

from alertaclient.utils import build_query


@click.command('ack', short_help='Close alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--text', help='Message associated with status change')
@click.pass_obj
def cli(obj, ids, filters, text):
    """Set alert status to 'closed'."""
    client = obj['client']
    if ids:
        total = len(ids)
    else:
        query = build_query(filters)
        total, _, _ = client.get_count(query)
        ids = [a.id for a in client.get_alerts(query)]

    with click.progressbar(ids, label='Closing {} alerts'.format(total)) as bar:
        for id in bar:
            client.set_status(id, status='closed', text=text or 'status changed using CLI')
