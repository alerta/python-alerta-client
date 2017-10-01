import os
import platform
import sys

import click

prog = os.path.basename(sys.argv[0])


@click.command('heartbeat', short_help='send a heartbeat')
@click.option('--origin', default='{}/{}'.format(prog, platform.uname()[1]))
@click.option('--tag', '-T', 'tags', multiple=True)
@click.option('--timeout', metavar='EXPIRES', help='seconds before heartbeat is stale')
@click.option('--delete', '-D', metavar='ID', help='delete hearbeat')
@click.pass_obj
def cli(obj, origin, tags, timeout, delete):
    """Send or delete a heartbeat."""
    client = obj['client']
    if delete:
        if origin or tags or timeout:
            raise click.UsageError('Option "--delete" is mutually exclusive.')
        client.delete_heartbeat(delete)
    else:
        try:
            heartbeat = client.heartbeat(origin=origin, tags=tags, timeout=timeout)
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(heartbeat.id)
