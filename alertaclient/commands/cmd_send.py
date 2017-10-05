
import sys

import click


@click.command('send', short_help='Send an alert')
@click.option('--resource', '-r', metavar='RESOURCE', required=True, help='Resource under alarm')
@click.option('--event', '-e', metavar='EVENT', required=True, help='Event name')
@click.option('--environment', '-E', metavar='ENVIRONMENT', help='Environment eg. Production, Development')
@click.option('--severity', '-s', metavar='SEVERITY', help='Severity eg. critical, major, minor, warning')
@click.option('--correlate', '-C', metavar='EVENT', multiple=True, help='List of related events eg. node_up, node_down')
@click.option('--service', '-S', metavar='SERVICE', multiple=True, help='List of affected services eg. app name, Web, Network, Storage, Database, Security')
@click.option('--group', '-g', metavar='GROUP', help='Group event by type eg. OS, Performance')
@click.option('--value', '-v', metavar='VALUE', help='Event value')
@click.option('--text', '-t', metavar='DESCRIPTION', help='Description of alert')
@click.option('--tag', '-T', 'tags', multiple=True, metavar='TAG', help='List of tags eg. London, os:linux, AWS/EC2')
@click.option('--attributes', '-A', multiple=True, metavar='KEY=VALUE', help='List of attributes eg. priority=high')
@click.option('--origin', '-O', metavar='ORIGIN', help='Origin of alert in form app/host')
@click.option('--type', metavar='EVENT_TYPE', help='Event type eg. exceptionAlert, performanceAlert, nagiosAlert')
@click.option('--timeout', metavar='EXPIRES', type=int, help='Seconds before an open alert will be expired')
@click.option('--raw-data', metavar='STRING', help='Raw data of orignal alert eg. SNMP trap PDU')
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
