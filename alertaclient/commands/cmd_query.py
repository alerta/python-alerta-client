import json

import click
from tabulate import tabulate

from alertaclient.models.alert import Alert
from alertaclient.utils import DateTime, build_query

COLOR_MAP = {
    'critical': {'fg': 'red'},
    'major': {'fg': 'magenta'},
    'minor': {'fg': 'yellow'},
    'warning': {'fg': 'blue'},
    'normal': {'fg': 'green'},
    'indeterminate': {'fg': 'cyan'},
}


@click.command('query', short_help='Search for alerts')
@click.option('--ids', '-i', metavar='ID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--query', '-q', 'query', metavar='QUERY', help='severity:"warning" AND resource:web')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--oneline', 'display', flag_value='oneline', default=True, help='Show alerts using table format')
@click.option('--medium', 'display', flag_value='medium', help='Show important alert attributes')
@click.option('--full', 'display', flag_value='full', help='Show full alert details')
@click.pass_obj
def cli(obj, ids, query, filters, display, from_date=None):
    """Query for alerts based on search filter criteria."""
    client = obj['client']
    timezone = obj['timezone']
    if ids:
        query = [('id', x) for x in ids]
    elif query:
        query = [('q', query)]
    else:
        query = build_query(filters)
    if from_date:
        query.append(('from-date', from_date))

    r = client.http.get('/alerts', query, page=1, page_size=1000)

    if obj['output'] == 'json':
        click.echo(json.dumps(r['alerts'], sort_keys=True, indent=4, ensure_ascii=False))
    elif obj['output'] in ['json_lines', 'jsonl', 'ndjson']:
        for alert in r['alerts']:
            click.echo(json.dumps(alert, ensure_ascii=False))
    else:
        alerts = [Alert.parse(a) for a in r['alerts']]
        last_time = r['lastTime']
        auto_refresh = r['autoRefresh']

        if display == 'oneline':
            headers = {'id': 'ID', 'lastReceiveTime': 'LAST RECEIVED', 'severity': 'SEVERITY', 'status': 'STATUS',
                       'duplicateCount': 'DUPL', 'customer': 'CUSTOMER', 'environment': 'ENVIRONMENT', 'service': 'SERVICE',
                       'resource': 'RESOURCE', 'group': 'GROUP', 'event': 'EVENT', 'value': 'VALUE', 'text': 'DESCRIPTION'}

            data = [{k: v for k, v in a.tabular(timezone).items() if k in headers.keys()} for a in alerts]
            click.echo(tabulate(data, headers=headers, tablefmt=obj['output']))

        else:
            for alert in reversed(alerts):
                color = COLOR_MAP.get(alert.severity, {'fg': 'white'})
                click.secho('{}|{}|{}|{:5d}|{}|{:<5s}|{:<10s}|{:<18s}|{:12s}|{:16s}|{:12s}'.format(
                    alert.id[0:8],
                    DateTime.localtime(alert.last_receive_time, timezone),
                    alert.severity,
                    alert.duplicate_count,
                    alert.customer or '-',
                    alert.environment,
                    ','.join(alert.service),
                    alert.resource,
                    alert.group,
                    alert.event,
                    alert.value or 'n/a'), fg=color['fg'])
                click.secho('   |{}'.format(alert.text), fg=color['fg'])

                if display == 'full':
                    click.secho('    severity   | {} -> {}'.format(alert.previous_severity,
                                                                   alert.severity), fg=color['fg'])
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

                    click.secho('        time created  | {}'.format(
                        DateTime.localtime(alert.create_time, timezone)), fg=color['fg'])
                    click.secho('        time received | {}'.format(
                        DateTime.localtime(alert.receive_time, timezone)), fg=color['fg'])
                    click.secho('        last received | {}'.format(
                        DateTime.localtime(alert.last_receive_time, timezone)), fg=color['fg'])
                    click.secho('        latency       | {}ms'.format(latency.microseconds / 1000), fg=color['fg'])
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
