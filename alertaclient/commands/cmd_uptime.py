from datetime import datetime, timedelta

import click


@click.command('uptime', short_help='Display server uptime')
@click.pass_obj
def cli(obj):
    """Display API server uptime in days, hours."""
    client = obj['client']
    status = client.mgmt_status()

    now = datetime.fromtimestamp(int(status['time']) / 1000.0)
    uptime = datetime(1, 1, 1) + timedelta(seconds=int(status['uptime']) / 1000.0)

    click.echo('{} up {} days {:02d}:{:02d}'.format(
        now.strftime('%H:%M'),
        uptime.day - 1, uptime.hour, uptime.minute
    ))
