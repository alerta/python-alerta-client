import re

import click

from alertaclient.utils import build_query


@click.command('action', short_help='Action alerts')
@click.option('--action', '-a', metavar='ACTION', help='Custom action (user-defined)')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--query', '-q', 'query', metavar='QUERY', help='severity:"warning" AND resource:web')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--text', help='Message associated with action')
@click.pass_obj
def cli(obj, action, ids, query, filters, text):
    """Take action on alert'."""
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

    action_text = re.sub('([A-Z])', r' \1', action).title()  # 'createIssue' => 'Create Issue'
    with click.progressbar(ids, label='Action {} {} alerts'.format(action, total)) as bar:
        for id in bar:
            client.action(id, action=action, text=text or '{} using CLI'.format(action_text))
