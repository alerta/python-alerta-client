
import click
from tabulate import tabulate

from alertaclient.models.alert import Alert
from alertaclient.utils import build_query, DateTime

COLOR_MAP = {
    'critical': {'fg': 'red'},
    'major': {'fg': 'magenta'},
    'minor': {'fg': 'yellow'},
    'warning': {'fg': 'blue'},
    'normal': {'fg': 'green'},
    'indeterminate': {'fg': 'cyan'},
}


@click.command('query', short_help='Search for alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--compact/--no-compact', default=True, help='Show alert details')
@click.pass_obj
def cli(obj, ids, filters, compact, from_date=None):
    """Query for alerts based on search filter criteria."""
    client = obj['client']
    timezone = obj['timezone']
    if ids:
        query = [('id', x) for x in ids]
    else:
        query = build_query(filters)
    if from_date:
        query.append(('from-date', from_date))

    r = client.http.get('/alerts', query)
    alerts = [Alert.parse(a) for a in r['alerts']]
    last_time = r['lastTime']
    auto_refresh = r['autoRefresh']

    if not compact:
        headers = {'id': 'ID', 'lastReceiveTime': 'LAST RECEIVED', 'severity': 'SEVERITY', 'duplicateCount': 'DUPL',
                   'customer': 'CUSTOMER', 'environment': 'ENVIRONMENT', 'service': 'SERVICE', 'resource': 'RESOURCE',
                   'group': 'GROUP', 'event': 'EVENT', 'value': 'VALUE'}
        click.echo(tabulate([a.tabular('summary', timezone) for a in alerts], headers=headers, tablefmt=obj['output']))
    else:
        for alert in reversed(alerts):
            color = COLOR_MAP.get(alert.severity, {'fg': 'white'})
            click.secho('{0}|{1}|{2}|{3:5d}|{4}|{5:<5s}|{6:<10s}|{7:<18s}|{8:12s}|{9:16s}|{10:12s}'.format(
                alert.id[0:8],
                DateTime.localtime(alert.last_receive_time, timezone),
                alert.severity,
                alert.duplicate_count,
                alert.customer or "-",
                alert.environment,
                ','.join(alert.service),
                alert.resource,
                alert.group,
                alert.event,
                alert.value or "n/a"), fg=color['fg'])
            click.secho('   |{}'.format(alert.text), fg=color['fg'])

            if True: # args.details:
                click.secho('    severity   | {} -> {}'.format(alert.previous_severity, alert.severity), fg=color['fg'])
                click.secho('    trend      | {}'.format(alert.trend_indication), fg=color['fg'])
                click.secho('    status     | {}'.format(alert.status), fg=color['fg'])
                click.secho('    resource   | {}'.format(alert.resource), fg=color['fg'])
                click.secho('    group      | {}'.format(alert.group), fg=color['fg'])
                click.secho('    event      | {}'.format(alert.event), fg=color['fg'])
                click.secho('    value      | {}'.format(alert.value), fg=color['fg'])
                click.secho('    tags       | {}'.format(' '.join(alert.tags)), fg=color['fg'])

                for key, value in alert.attributes.items():
                    click.secho('    {} | {}'.format(key.ljust(10), value), fg=color['fg'])

                latency = alert.receive_time - alert.create_time

                click.secho('        time created  | {}'.format(DateTime.localtime(alert.create_time, timezone)), fg=color['fg'])
                click.secho('        time received | {}'.format(DateTime.localtime(alert.receive_time, timezone)), fg=color['fg'])
                click.secho('        last received | {}'.format(DateTime.localtime(alert.last_receive_time, timezone)), fg=color['fg'])
                click.secho('        latency       | {}ms'.format((latency.microseconds / 1000)), fg=color['fg'])
                click.secho('        timeout       | {}s'.format(alert.timeout), fg=color['fg'])

                click.secho('            alert id     | {}'.format(alert.id), fg=color['fg'])
                click.secho('            last recv id | {}'.format(alert.last_receive_id), fg=color['fg'])
                click.secho('            customer     | {}'.format(alert.customer), fg=color['fg'])
                click.secho('            environment  | {}'.format(alert.environment), fg=color['fg'])
                click.secho('            service      | {}'.format(','.join(alert.service)), fg=color['fg'])
                click.secho('            resource     | {}'.format(alert.resource), fg=color['fg'])
                click.secho('            type         | {}'.format(alert.event_type), fg=color['fg'])
                click.secho('            repeat       | {}'.format(alert.repeat), fg=color['fg'])
                click.secho('            origin       | {}'.format(alert.origin), fg=color['fg'])
                click.secho('            correlate    | {}'.format(','.join(alert.correlate)), fg=color['fg'])

    return auto_refresh, last_time
