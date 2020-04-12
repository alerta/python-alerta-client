import json
import os
import sys

import click


@click.command('send', short_help='Send an alert')
@click.option('--resource', '-r', metavar='RESOURCE', required=False, help='Resource under alarm')
@click.option('--event', '-e', metavar='EVENT', required=False, help='Event name')
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
@click.option('--timeout', metavar='SECONDS', type=int, help='Seconds before an open alert will be expired')
@click.option('--raw-data', metavar='STRING', help='Raw data of orignal alert eg. SNMP trap PDU. \'@\' to read from file, \'-\' to read from stdin')
@click.option('--customer', metavar='STRING', help='Customer')
@click.pass_obj
def cli(obj, resource, event, environment, severity, correlate, service, group, value, text, tags, attributes, origin, type, timeout, raw_data, customer):
    """Send an alert."""
    client = obj['client']

    def send_alert(resource, event, **kwargs):
        try:
            id, alert, message = client.send_alert(
                resource=resource,
                event=event,
                environment=kwargs.get('environment'),
                severity=kwargs.get('severity'),
                correlate=kwargs.get('correlate', None) or list(),
                service=kwargs.get('service', None) or list(),
                group=kwargs.get('group'),
                value=kwargs.get('value'),
                text=kwargs.get('text'),
                tags=kwargs.get('tags', None) or list(),
                attributes=kwargs.get('attributes', None) or dict(),
                origin=kwargs.get('origin'),
                type=kwargs.get('type'),
                timeout=kwargs.get('timeout'),
                raw_data=kwargs.get('raw_data'),
                customer=kwargs.get('customer')
            )
        except Exception as e:
            click.echo('ERROR: {}'.format(e), err=True)
            sys.exit(1)

        if alert:
            if alert.repeat:
                message = '{} duplicates'.format(alert.duplicate_count)
            else:
                message = '{} -> {}'.format(alert.previous_severity, alert.severity)
        click.echo('{} ({})'.format(id, message))

    # read raw data from file or stdin
    if raw_data and raw_data.startswith('@') or raw_data == '-':
        raw_data_file = raw_data.lstrip('@')
        with click.open_file(raw_data_file, 'r') as f:
            raw_data = f.read()

    # read entire alert object from terminal stdin
    elif not sys.stdin.isatty() and (os.environ.get('TERM', None) or os.environ.get('PS1', None)):
        with click.get_text_stream('stdin') as stdin:
            for line in stdin.readlines():
                try:
                    payload = json.loads(line)
                except Exception as e:
                    click.echo("ERROR: JSON parse failure - input must be in 'json_lines' format: {}".format(e), err=True)
                    sys.exit(1)
                send_alert(**payload)
            sys.exit(0)

    send_alert(
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
        attributes=dict(a.split('=', maxsplit=1) if '=' in a else (a, None) for a in attributes),
        origin=origin,
        type=type,
        timeout=timeout,
        raw_data=raw_data,
        customer=customer
    )
