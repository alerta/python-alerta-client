import click

from alertaclient.utils import build_query


@click.command('delete', short_help='Delete alerts')
@click.option('--ids', '-i', metavar='ID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--query', '-q', 'query', metavar='QUERY', help='severity:"warning" AND resource:web')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.pass_obj
def cli(obj, ids, query, filters):
    """Delete alerts."""
    client = obj['client']
    if ids:
        total = len(ids)
    else:
        if not (query or filters):
            click.confirm('Deleting all alerts. Do you want to continue?', abort=True)
        if query:
            query = [('q', query)]
        else:
            query = build_query(filters)
        total, _, _ = client.get_count(query)
        ids = [a.id for a in client.get_alerts(query)]

    with click.progressbar(ids, label='Deleting {} alerts'.format(total)) as bar:
        for id in bar:
            client.delete_alert(id)
