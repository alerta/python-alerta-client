import sys

import click

from alertaclient.utils import origin


@click.command('heartbeat', short_help='Send a heartbeat')
@click.option('--origin', '-O', metavar='ORIGIN', default=origin, help='Origin of heartbeat.')
@click.option('--environment', '-E', metavar='ENVIRONMENT', help='Environment eg. Production, Development')
@click.option('--severity', '-s', metavar='SEVERITY', help='Severity eg. critical, major, minor, warning')
@click.option('--service', '-S', metavar='SERVICE', multiple=True, help='List of affected services eg. app name, Web, Network, Storage, Database, Security')
@click.option('--group', '-g', metavar='GROUP', help='Group event by type eg. OS, Performance')
@click.option('--tag', '-T', 'tags', multiple=True, metavar='TAG', help='List of tags eg. London, os:linux, AWS/EC2')
@click.option('--timeout', metavar='SECONDS', type=int, help='Seconds before heartbeat is stale')
@click.option('--customer', metavar='STRING', help='Customer')
@click.option('--delete', '-D', metavar='ID', help='Delete hearbeat using ID')
@click.pass_obj
def cli(obj, origin, environment, severity, service, group, tags, timeout, customer, delete):
    """
    Send or delete a heartbeat.

    Note: The "environment", "severity", "service" and "group" values are only
    used when heartbeat alerts are generated from slow or stale heartbeats.
    """
    client = obj['client']
    if delete:
        client.delete_heartbeat(delete)
    else:
        if any(t.startswith('environment') or t.startswith('group') for t in tags):
            click.secho('ERROR: Do not use tags for "environment" or "group". See help.', bold=True)

        attributes = dict()
        if environment:
            attributes['environment'] = environment
        if severity:
            attributes['severity'] = severity
        if service:
            attributes['service'] = service
        if group:
            attributes['group'] = group

        try:
            heartbeat = client.heartbeat(origin=origin, tags=tags, attributes=attributes, timeout=timeout, customer=customer)
        except Exception as e:
            click.echo('ERROR: {}'.format(e))
            sys.exit(1)
        click.echo(heartbeat.id)
