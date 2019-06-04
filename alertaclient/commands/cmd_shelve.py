import click

from alertaclient.utils import action_progressbar, build_query


@click.command('shelve', short_help='Shelve alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--query', '-q', 'query', metavar='QUERY', help='severity:"warning" AND resource:web')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--timeout', metavar='SECONDS', type=int, help='Seconds before alert auto-unshelved.', default=7200, show_default=True)
@click.option('--text', help='Message associated with status change')
@click.pass_obj
def cli(obj, ids, query, filters, timeout, text):
    """Set alert status to 'shelved'."""
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

    action_progressbar(client, action='shelve', ids=ids,
                       label='Shelving {} alerts'.format(total), text=text, timeout=timeout)
