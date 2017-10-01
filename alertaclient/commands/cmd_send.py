
import sys

import click


@click.command('send', short_help='send an alert')
@click.option('--resource', '-r', metavar='RESOURCE', required=True, help='resource under alarm')
@click.option('--event', '-e', metavar='EVENT', required=True, help='event name')
@click.option('--environment', '-E', metavar='ENVIRONMENT', help='environment eg. Production, Development')
@click.option('--severity', '-s', metavar='SEVERITY', help='severity eg. critical, major, minor, warning')
@click.option('--correlate', '-C', metavar='EVENT', multiple=True, help='list of related events eg. node_up, node_down')
@click.option('--service', '-S', metavar='SERVICE', multiple=True, help='list of affected services eg. app name, Web, Network, Storage, Database, Security')
@click.option('--group', '-g', metavar='GROUP', help='group event by type eg. OS, Performance')
@click.option('--value', '-v', metavar='VALUE', help='string event value')
@click.option('--text', '-t', metavar='DESCRIPTION', help='description of alert')
@click.option('--tag', '-T', 'tags', multiple=True, metavar='TAG', help='list of tags eg. London, os:linux, AWS/EC2')
@click.option('--attributes', '-A', multiple=True, metavar='KEY=VALUE', help='list of attributes eg. priority=high')
@click.option('--origin', '-O', metavar='ORIGIN', help='origin of alert in form app/host')
@click.option('--type', metavar='EVENT_TYPE', help='event type eg. exceptionAlert, performanceAlert, nagiosAlert')
@click.option('--timeout', metavar='EXPIRES', help='seconds before an open alert will be expired')
@click.option('--raw-data', metavar='STRING', help='raw data of orignal alert eg. SNMP trap PDU')
@click.pass_obj
def cli(obj, resource, event, environment, severity, correlate, service, group, value, text, tags, attributes, origin, type, timeout, raw_data):
    """Send an alert."""
    client = obj['client']
    try:
        alert = client.send_alert(
            resource=resource,
            event=event,
            environment=environment,
            severity=severity,
            correlate=correlate,
            service=service,
            group=group,
            value=value,
            text=text,
            tags=tags,
            attributes=dict(a.split('=') for a in attributes),
            origin=origin,
            type=type,
            timeout=timeout,
            raw_data=raw_data
        )
    except Exception as e:
        click.echo('ERROR: {}'.format(e))
        sys.exit(1)
    if alert.repeat:
        click.echo('{} ({} duplicates)'.format(alert.id, alert.duplicate_count))
    else:
        click.echo('{} {} -> {}'.format(alert.id, alert.previous_severity, alert.severity))
