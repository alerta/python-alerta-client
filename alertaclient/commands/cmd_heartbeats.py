import json

import click
from tabulate import tabulate

from alertaclient.models.heartbeat import Heartbeat
from alertaclient.utils import origin


@click.command('heartbeats', short_help='List heartbeats')
@click.option('--alert', is_flag=True, help='Alert on stale or slow heartbeats')
@click.option('--severity', '-s', metavar='SEVERITY', default='major', help='Severity for stale heartbeat alerts')
@click.option('--timeout', metavar='SECONDS', default=86000, type=int, help='Seconds before stale heartbeat alerts will be expired')
@click.option('--purge', is_flag=True, help='Delete all stale heartbeats')
@click.pass_obj
def cli(obj, alert, severity, timeout, purge):
    """List heartbeats."""
    client = obj['client']

    try:
        default_normal_severity = obj['alarm_model']['defaults']['normal_severity']
    except KeyError:
        default_normal_severity = 'normal'

    if obj['output'] == 'json':
        r = client.http.get('/heartbeats')
        heartbeats = [Heartbeat.parse(hb) for hb in r['heartbeats']]
        click.echo(json.dumps(r['heartbeats'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        timezone = obj['timezone']
        headers = {
            'id': 'ID', 'origin': 'ORIGIN', 'customer': 'CUSTOMER', 'tags': 'TAGS', 'attributes': 'ATTRIBUTES',
            'createTime': 'CREATED', 'receiveTime': 'RECEIVED', 'since': 'SINCE', 'timeout': 'TIMEOUT',
            'latency': 'LATENCY', 'maxLatency': 'MAX LATENCY', 'status': 'STATUS'
        }
        heartbeats = client.get_heartbeats()
        click.echo(tabulate([h.tabular(timezone) for h in heartbeats], headers=headers, tablefmt=obj['output']))

    not_ok = [hb for hb in heartbeats if hb.status != 'ok']
    if purge:
        with click.progressbar(not_ok, label='Purging {} heartbeats'.format(len(not_ok))) as bar:
            for b in bar:
                client.delete_heartbeat(b.id)

    if alert:
        with click.progressbar(heartbeats, label='Alerting {} heartbeats'.format(len(heartbeats))) as bar:
            for b in bar:
                if b.status == 'expired':  # aka. "stale"
                    client.send_alert(
                        resource=b.origin,
                        event='HeartbeatFail',
                        environment=b.attributes.get('environment', 'Production'),
                        severity=b.attributes.get('severity', severity),
                        correlate=['HeartbeatFail', 'HeartbeatSlow', 'HeartbeatOK'],
                        service=b.attributes.get('service', ['Alerta']),
                        group=b.attributes.get('group', 'System'),
                        value='{}'.format(b.since),
                        text='Heartbeat not received in {} seconds'.format(b.timeout),
                        tags=b.tags,
                        attributes=b.attributes,
                        origin=origin(),
                        type='heartbeatAlert',
                        timeout=timeout,
                        customer=b.customer
                    )
                elif b.status == 'slow':
                    client.send_alert(
                        resource=b.origin,
                        event='HeartbeatSlow',
                        environment=b.attributes.get('environment', 'Production'),
                        severity=b.attributes.get('severity', severity),
                        correlate=['HeartbeatFail', 'HeartbeatSlow', 'HeartbeatOK'],
                        service=b.attributes.get('service', ['Alerta']),
                        group=b.attributes.get('group', 'System'),
                        value='{}ms'.format(b.latency),
                        text='Heartbeat took more than {}ms to be processed'.format(b.max_latency),
                        tags=b.tags,
                        attributes=b.attributes,
                        origin=origin(),
                        type='heartbeatAlert',
                        timeout=timeout,
                        customer=b.customer
                    )
                else:
                    client.send_alert(
                        resource=b.origin,
                        event='HeartbeatOK',
                        environment=b.attributes.get('environment', 'Production'),
                        severity=b.attributes.get('severity', default_normal_severity),
                        correlate=['HeartbeatFail', 'HeartbeatSlow', 'HeartbeatOK'],
                        service=b.attributes.get('service', ['Alerta']),
                        group=b.attributes.get('group', 'System'),
                        value='',
                        text='Heartbeat OK',
                        tags=b.tags,
                        attributes=b.attributes,
                        origin=origin(),
                        type='heartbeatAlert',
                        timeout=timeout,
                        customer=b.customer
                    )
