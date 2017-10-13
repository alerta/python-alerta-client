
import sys
import time
import click

from .cmd_query import cli as query


@click.command('watch', short_help='Watch alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--compact/--no-compact', default=True, help='Show alert details')
@click.option('--interval', '-n', type=int, default=2, help='Interval in seconds')
@click.pass_context
def cli(ctx, ids, filters, compact, interval):
    """Query for alerts based on search filter criteria."""
    auto_refresh = True
    from_date = None

    while auto_refresh:
        try:
            auto_refresh, from_date = ctx.invoke(query, ids=ids, filters=filters, compact=compact, from_date=from_date)
            time.sleep(interval)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
