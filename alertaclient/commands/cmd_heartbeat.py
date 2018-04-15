import os
import platform
import sys

import click

prog = os.path.basename(sys.argv[0])


@click.command('heartbeat', short_help='Send a heartbeat')
@click.option('--origin', '-O', metavar='ORIGIN', default='{}/{}'.format(prog, platform.uname()[1]), help='Origin of heartbeat.')
@click.option('--tag', '-T', 'tags', multiple=True, metavar='TAG', help='List of tags eg. London, os:linux, AWS/EC2')
@click.option('--timeout', metavar='SECONDS', type=int, help='Seconds before heartbeat is stale')
@click.option('--customer', metavar='STRING', help='Customer')
@click.option('--delete', '-D', metavar='ID', help='Delete hearbeat using ID')
@click.pass_obj
def cli(obj, origin, tags, timeout, customer, delete):
    """Send or delete a heartbeat."""
    client = obj['client']
    if delete:
        client.delete_heartbeat(delete)
    else:
        try:
            heartbeat = client.heartbeat(origin=origin, tags=tags, timeout=timeout, customer=customer)
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(heartbeat.id)
