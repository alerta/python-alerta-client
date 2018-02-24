
import json

import click
from tabulate import tabulate

from alertaclient.models.heartbeat import MAX_LATENCY


@click.command('heartbeats', short_help='List heartbeats')
@click.option('--alert', is_flag=True, help='Alert on stale or slow heartbeats')
@click.option('--severity', '-s', metavar='SEVERITY', default='major', help='Severity for stale heartbeat alerts')
@click.option('--purge', is_flag=True, help='Delete all stale heartbeats')
@click.pass_obj
def cli(obj, alert, severity, purge):
    """List heartbeats."""
    client = obj['client']

    if obj['output'] == 'json':
        r = client.http.get('/heartbeats')
        click.echo(json.dumps(r['heartbeats'], sort_keys=True, indent=4, ensure_ascii=False))
    else:
        timezone = obj['timezone']
        headers = {
            'id': 'ID', 'origin': 'ORIGIN', 'customer': 'CUSTOMER', 'tags': 'TAGS', 'createTime': 'CREATED',
            'receiveTime': 'RECEIVED', 'latency': 'LATENCY', 'timeout': 'TIMEOUT', 'since': 'SINCE', 'status': 'STATUS'
        }
        heartbeats = client.get_heartbeats()
        click.echo(tabulate([h.tabular(timezone) for h in heartbeats], headers=headers, tablefmt=obj['output']))

        not_ok = [hb for hb in heartbeats if hb.status != 'ok']
        if purge:
            with click.progressbar(not_ok, label='Purging {} heartbeats'.format(len(not_ok))) as bar:
                for b in bar:
                    client.delete_heartbeat(b.id)

        elif alert:
            with click.progressbar(heartbeats, label='Alerting {} heartbeats'.format(len(heartbeats))) as bar:
                for b in bar:
                    params = dict(filter(lambda a: len(a) == 2, map(lambda a: a.split(':'), b.tags)))
                    environment = params.get('environment', 'Production')
                    group = params.get('group', 'System')
                    tags = list(filter(lambda a: not a.startswith('environment:') and not a.startswith('group:'), b.tags))

                    if b.status == 'expired':  # aka. "stale"
                        client.send_alert(
                            resource=b.origin,
                            event='HeartbeatFail',
                            correlate=['HeartbeatFail', 'HeartbeatSlow', 'HeartbeatOK'],
                            group=group,
                            environment=environment,
                            service=['Alerta'],
                            severity=severity,
                            value='{}'.format(b.since),
                            text='Heartbeat not received in {} seconds'.format(b.timeout),
                            tags=tags,
                            type='heartbeatAlert'
                        )
                    elif b.status == 'slow':
                        client.send_alert(
                            resource=b.origin,
                            event='HeartbeatSlow',
                            correlate=['HeartbeatFail', 'HeartbeatSlow', 'HeartbeatOK'],
                            group=group,
                            environment=environment,
                            service=['Alerta'],
                            severity=severity,
                            value='{}ms'.format(b.latency),
                            text='Heartbeat took more than {}ms to be processed'.format(MAX_LATENCY),
                            tags=tags,
                            type='heartbeatAlert'
                        )
                    else:
                        client.send_alert(
                            resource=b.origin,
                            event='HeartbeatOK',
                            correlate=['HeartbeatFail', 'HeartbeatSlow', 'HeartbeatOK'],
                            group=group,
                            environment=environment,
                            service=['Alerta'],
                            severity='normal',
                            value='',
                            text='Heartbeat OK',
                            tags=tags,
                            type='heartbeatAlert'
                        )
