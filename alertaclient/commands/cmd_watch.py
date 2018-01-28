
import sys
import time
import click

from .cmd_query import cli as query


@click.command('watch', short_help='Watch alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--details', is_flag=True, help='Compact output with details')
@click.option('--interval', '-n', metavar='SECONDS', type=int, default=2, help='Refresh interval')
@click.pass_context
def cli(ctx, ids, filters, details, interval):
    """Query for alerts based on search filter criteria."""
    if details:
        display = 'details'
    else:
        display = 'compact'
    from_date = None

    auto_refresh = True
    while auto_refresh:
        try:
            auto_refresh, from_date = ctx.invoke(query, ids=ids, filters=filters, display=display, from_date=from_date)
            time.sleep(interval)
        except (KeyboardInterrupt, SystemExit) as e:
            sys.exit(e)
