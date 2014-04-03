
import os
import sys
import argparse
import time
# import pytz
import datetime
import ConfigParser
import json
import logging

from client import ApiClient
from alert import Alert
from heartbeat import Heartbeat

LOG = logging.getLogger('alerta')

__version__ = '3.0.2'

DEFAULT_CONF_FILE = '~/.alerta.conf'
DEFAULT_ENDPOINT_URL = 'http://localhost:8080/api'
DEFAULT_OUTPUT = 'text'
DEFAULT_TIMEZONE = 'Europe/London'

_COLOR_MAP = {
    "critical": '\033[91m',
    "major": '\033[95m',
    "minor": '\033[93m',
    "warning": '\033[96m',
    "indeterminate": '\033[92m',
    "clear": '\033[92m',
    "normal": '\033[92m',
    "informational": '\033[92m',
    "debug": '\033[90m',
    "auth": '\033[90m',
    "unknown": '\033[90m',
}
_ENDC = '\033[0m'

NOT_SET = '<not set>'


class AlertCommand(object):

    def __init__(self):

        self.api = None

    def set_api(self, url):

        self.api = ApiClient(endpoint=url)

    def send(self, args):

        try:
            alert = Alert(
                resource=args.resource,
                event=args.event,
                environment=args.environment,
                severity=args.severity,
                correlate=args.correlate,
                status=args.status,
                service=args.service,
                group=args.group,
                value=args.value,
                text=args.text,
                tags=args.tags,
                attributes=dict([attrib.split('=') for attrib in args.attributes]),
                origin=args.origin,
                event_type=args.event_type,
                timeout=args.timeout,
                raw_data=args.raw_data
            )
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        try:
            response = self.api.send(alert)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == 'ok':
            print response['id']
        else:
            LOG.error(response['message'])
            sys.exit(1)

    def heartbeat(self, args):

        try:
            heartbeat = Heartbeat(
                origin=args.origin,
                tags=args.tags,
                timeout=args.timeout
            )
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        try:
            response = self.api.send(heartbeat)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == 'ok':
            print response['id']
        else:
            LOG.error(response['message'])
            sys.exit(1)

    def query(self, args, from_date=None):

        response = self._alerts(args.filter, from_date)
        alerts = response['alerts']

        if args.output == "json":
            print json.dumps(alerts, indent=4)
            sys.exit(0)

        # tz = pytz.timezone(args.timezone)

        for alert in reversed(alerts):
            line_color = ''
            end_color = _ENDC

            last_receive_time = datetime.datetime.strptime(alert.get('lastReceiveTime', None), '%Y-%m-%dT%H:%M:%S.%fZ')
            # last_receive_time = last_receive_time.replace(tzinfo=pytz.utc)

            if args.color:
                line_color = _COLOR_MAP[alert['severity']]

            print(line_color + '%s|%s|%s|%5d|%-5s|%-10s|%-18s|%12s|%16s|%12s' % (
                alert['id'][0:8],
                # last_receive_time.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S'),
                last_receive_time.strftime('%Y/%m/%d %H:%M:%S'),
                alert['severity'],
                alert['duplicateCount'],
                alert.get('environment', NOT_SET),
                ','.join(alert.get('service', [NOT_SET])),
                alert['resource'],
                alert.get('group', NOT_SET),
                alert['event'],
                alert.get('value', NOT_SET) + end_color)
            )
            print(line_color + '   |%s' % (alert['text'].encode('utf-8')) + end_color)

            if args.details:
                print(
                    line_color + '    severity   | %s -> %s' % (
                        alert['previousSeverity'],
                        alert['severity']) + end_color)
                print(line_color + '    trend      | %s' % alert['trendIndication'] + end_color)
                print(line_color + '    status     | %s' % alert['status'] + end_color)
                print(line_color + '    resource   | %s' % alert['resource'] + end_color)
                print(line_color + '    group      | %s' % alert['group'] + end_color)
                print(line_color + '    event      | %s' % alert['event'] + end_color)
                print(line_color + '    value      | %s' % alert['value'] + end_color)
                print(line_color + '    tags       | %s' % ' '.join(alert['tags']) + end_color)

                for key, value in alert['attributes'].items():
                    print(line_color + '    %s | %s' % (key.ljust(10), value) + end_color)

                print(line_color + '        time created  | %s' % (
                    alert['createTime'] + end_color))
                print(line_color + '        time received | %s' % (
                    alert['receiveTime']) + end_color)
                print(line_color + '        last received | %s' % (
                    alert['lastReceiveTime']) + end_color)
                #print(line_color + '        latency       | %sms' % latency + end_color)
                print(line_color + '        timeout       | %ss' % alert['timeout'] + end_color)

                print(line_color + '            alert id     | %s' % alert['id'] + end_color)
                print(line_color + '            last recv id | %s' % alert['lastReceiveId'] + end_color)
                print(line_color + '            environment  | %s' % alert['environment'] + end_color)
                print(line_color + '            service      | %s' % (','.join(alert['service'])) + end_color)
                print(line_color + '            resource     | %s' % alert['resource'] + end_color)
                print(line_color + '            type         | %s' % alert['type'] + end_color)
                print(line_color + '            repeat       | %s' % alert['repeat'] + end_color)
                print(line_color + '            origin       | %s' % alert['origin'] + end_color)
                print(line_color + '            correlate    | %s' % (','.join(alert['correlate'])) + end_color)

        return response.get('lastTime', '')

    def watch(self, args):

        from_date = None
        while True:
            from_date = self.query(args, from_date)
            try:
                time.sleep(2)
            except (KeyboardInterrupt, SystemExit):
                sys.exit(0)

    def raw(self, args):

        response = self._alerts(args.filter)
        alerts = response['alerts']

        if args.output == "json":
            print json.dumps(alerts, indent=4)
            sys.exit(0)

        for alert in reversed(alerts):
            line_color = ''
            end_color = _ENDC

            print(line_color + alert['rawData'] + end_color)

    def history(self, args):

        response = self._history(args.filter)
        history = response['history']

        if args.output == "json":
            print json.dumps(history, indent=4)
            sys.exit(0)

        # tz = pytz.timezone(args.timezone)

        for hist in history:

            line_color = ''
            end_color = _ENDC

            update_time = datetime.datetime.strptime(hist.get('updateTime', None), '%Y-%m-%dT%H:%M:%S.%fZ')

            if 'severity' in hist:
                if args.color:
                    line_color = _COLOR_MAP[hist['severity']]
                print(line_color + '%s|%s|%s|%-5s|%-10s|%-18s|%s|%s|%s|%s' % (
                    hist['id'][0:8],
                    update_time.strftime('%Y/%m/%d %H:%M:%S'),
                    hist['severity'],
                    hist['environment'],
                    ','.join(hist['service']),
                    hist['resource'],
                    hist['group'],
                    hist['event'],
                    hist['value'],
                    hist['text']
                ) + end_color)

            if 'status' in hist:
                print(line_color + '%s|%s|%s|%-5s|%-10s|%-18s|%s|%s|%s|%s' % (
                    hist['id'][0:8],
                    update_time.strftime('%Y/%m/%d %H:%M:%S'),
                    hist['status'],
                    hist['environment'],
                    ','.join(hist['service']),
                    hist['resource'],
                    hist['group'],
                    hist['event'],
                    'n/a',
                    hist['text']
                ) + end_color)

    def tag(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Tagging alerts: ")
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.tag_alert(alert['id'], args.tags)

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def ack(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Acking alerts: ")
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.ack_alert(alert['id'])

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def unack(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("un-Acking alerts: ")
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.unack_alert(alert['id'])

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def close(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Closing alerts: ")
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.close_alert(alert['id'])

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def delete(self, args):

        sys.stdout.write("Counting alerts: ")
        response = self._alerts(args.filter)
        alerts = response['alerts']
        total = response['total']
        sys.stdout.write("%s, done.\n" % total)

        sys.stdout.write("Deleting alerts: ")
        for i, alert in enumerate(alerts):
            pct = int(100.0 * i / total)
            sys.stdout.write("%3d%% (%d/%d)" % (pct, i, total))
            sys.stdout.flush()
            sys.stdout.write("\b" * (8 + len(str(i)) + len(str(total))))
            self.api.delete_alert(alert['id'])

        sys.stdout.write("100%% (%d/%d), done.\n" % (total, total))

    def _alerts(self, filter, from_date=None):

        query = dict([x.split('=', 1) for x in filter if '=' in x])

        if from_date:
            query['from-date'] = from_date

        if 'sort-by' not in query:
            query['sort-by'] = 'lastReceiveTime'

        try:
            response = self.api.get_alerts(**query)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == "error":
            LOG.error(response['message'])
            sys.exit(1)

        return response

    def _history(self, filter, from_date=None):

        query = dict([x.split('=', 1) for x in filter if '=' in x])

        if from_date:
            query['from-date'] = from_date

        try:
            response = self.api.get_history(**query)
        except Exception as e:
            LOG.error(e)
            sys.exit(1)

        if response['status'] == "error":
            LOG.error(response['message'])
            sys.exit(1)

        return response

    def version(self, args):

        print 'alerta client %s' % __version__


def main():

    cli = AlertCommand()

    defaults = {
        'config_file': os.environ.get('ALERTA_CONF_FILE') or DEFAULT_CONF_FILE,
        'profile': os.environ.get('ALERTA_DEFAULT_PROFILE'),
        'endpoint': os.environ.get('ALERTA_DEFAULT_ENDPOINT') or DEFAULT_ENDPOINT_URL,
        'color': True if os.environ.get('CLICOLOR') else False,
        'timezone': DEFAULT_TIMEZONE,
        'output': DEFAULT_OUTPUT,
        'debug': False
    }

    profile_parser = argparse.ArgumentParser(
        add_help=False
    )
    profile_parser.add_argument(
        '--profile',
        default=defaults['profile'],
        help='Select profile to apply from %s' % defaults['config_file']
    )
    args, left = profile_parser.parse_known_args()

    config_file = defaults['config_file']
    if config_file:

        config = ConfigParser.SafeConfigParser(defaults=defaults)
        config.read(os.path.expanduser(config_file))

        defaults = dict(config.defaults())

        if args.profile:
            defaults['profile'] = args.profile
            for section in config.sections():
                if section.startswith('profile '):
                    if args.profile == section.replace('profile ', ''):
                        defaults['debug'] = config.getboolean(section, 'debug')
                        defaults['endpoint'] = config.get(section, 'endpoint')
                        defaults['output'] = config.get(section, 'output')
                        defaults['color'] = config.getboolean(section, 'color')
                        defaults['timezone'] = config.get(section, 'timezone')

    parser = argparse.ArgumentParser(
        prog='alert',
        usage='alert [OPTIONS] COMMAND [FILTERS]',
        description="Alerta client unified command-line tool",
        epilog='Filters:\n'
               '    Query parameters can be used to filter alerts by any valid alert attribute\n\n'
               '    resource=web01     Filter alerts by resource equal to "web01"\n'
               '    resource!=web01    Filter alerts by all resources except "web01"\n'
               '    event=~.*down      Filter alerts by event ending in "down"\n'
               '    event!=~.*down     Filter alerts by event not ending in "down"\n\n'
               '    Special query parameters include "limit", "sort-by", "from-date" and "q" (a\n'
               '    json-compliant mongo query).\n',
        formatter_class=argparse.RawTextHelpFormatter,
        parents=[profile_parser]
    )
    parser.set_defaults(**defaults)
    parser.add_argument(
        '--debug',
        action='store_true',
        help='debug mode'
    )
    parser.add_argument(
        '--endpoint-url',
        default=defaults['endpoint'],
        dest='endpoint',
        metavar='URL',
        help='endpoint URL'
    )
    parser.add_argument(
        '--output',
        default=defaults['output'],
        help='Output format of "text", "table" or "json"'
    )
    parser.add_argument(
        '--json',
        '-j',
        action='store_true',
        help='Output format of JSON. Shortcut for "--output json"'
    )
    parser.add_argument(
        '--color',
        '--colour',
        action='store_true',
        default=defaults['color'],
        help='Color-coded output based on severity'
    )
    parser.add_argument(
        '--no-color',
        '--no-colour',
        action='store_false',
        default=defaults['color'],
        dest='color',
        help=argparse.SUPPRESS
    )
    subparsers = parser.add_subparsers(
        title='Commands',
    )

    parser_send = subparsers.add_parser('send', help='Send alert to server')
    parser_send.add_argument(
        '-r',
        '--resource',
        help='resource under alarm'
    )
    parser_send.add_argument(
        '-e',
        '--event',
        help='event'
    )
    parser_send.add_argument(
        '-E',
        '--environment',
        help='environment eg. "production", "development", "testing"'
    )
    parser_send.add_argument(
        '-s',
        '--severity',
        help='severity'
    )
    parser_send.add_argument(
        '-C',
        '--correlate',
        action='append',
        help='correlate'
    )
    parser_send.add_argument(
        '--status',
        help='status should not normally be defined eg. "open", "closed"'
    )
    parser_send.add_argument(
        '-S',
        '--service',
        action='append',
        help='service affected eg. the application name, "Web", "Network", "Storage", "Database", "Security"'
    )
    parser_send.add_argument(
        '-g',
        '--group',
        help='group'
    )
    parser_send.add_argument(
        '-v',
        '--value',
        help='value'
    )
    parser_send.add_argument(
        '-t',
        '--text',
        help='Freeform alert text eg. "Host not responding to ping."'
    )
    parser_send.add_argument(
        '-T',
        '--tag',
        action='append',
        dest='tags',
        default=list(),
        help='List of tags eg. "London", "os:linux", "AWS/EC2".'
    )
    parser_send.add_argument(
        '-A',
        '--attribute',
        action='append',
        dest='attributes',
        default=list(),
        help='List of Key=Value attribute pairs eg. "priority=high", "moreInfo=..."'
    )
    parser_send.add_argument(
        '-O',
        '--origin',
        default=None,
        help='Origin of alert. Usually in form of "app/host"'
    )
    parser_send.add_argument(
        '--type',
        dest='event_type',
        default='exceptionAlert',
        help='event type eg. "exceptionAlert", "serviceAlert"'
    )
    parser_send.add_argument(
        '--timeout',
        default=None,
        help='Timeout in seconds before an "open" alert will be automatically "expired" or "deleted"'
    )
    parser_send.add_argument(
        '--raw-data',
        default=None,
        help='raw data'
    )
    parser_send.set_defaults(func=cli.send)

    parser_query = subparsers.add_parser('query', help='List alerts based on query filter')
    parser_query.add_argument(
        '--details',
        action='store_true',
        help='Show alert details'
    )
    parser_query.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. stack=soulmates'
    )
    parser_query.set_defaults(func=cli.query)

    parser_watch = subparsers.add_parser('watch', help='Watch alerts based on query filter')
    parser_watch.add_argument(
        '--details',
        action='store_true',
        help='Show alert details'
    )
    parser_watch.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. stack=soulmates'
    )
    parser_watch.set_defaults(func=cli.watch)

    parser_raw = subparsers.add_parser('raw', help='Show alert raw data')
    parser_raw.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. id=5108bc20'
    )
    parser_raw.set_defaults(func=cli.raw)

    parser_history = subparsers.add_parser('history', help='Show alert history')
    parser_history.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. id=5108bc20'
    )
    parser_history.set_defaults(func=cli.history)

    parser_tag = subparsers.add_parser('tag', help='Tag alerts')
    parser_tag.add_argument(
        '-T',
        '--tag',
        action='append',
        dest='tags',
        default=list(),
        help='List of tags eg. "London", "os:linux", "AWS/EC2".'
    )
    parser_tag.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. id=5108bc20'
    )
    parser_tag.set_defaults(func=cli.tag)

    parser_ack = subparsers.add_parser('ack', help='Acknowledge alerts')
    parser_ack.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. id=5108bc20'
    )
    parser_ack.set_defaults(func=cli.ack)

    parser_unack = subparsers.add_parser('unack', help='Unacknowledge alerts')
    parser_unack.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. id=5108bc20'
    )
    parser_unack.set_defaults(func=cli.unack)

    parser_close = subparsers.add_parser('close', help='Close alerts')
    parser_close.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. id=5108bc20'
    )
    parser_close.set_defaults(func=cli.close)

    parser_delete = subparsers.add_parser('delete', help='Delete alerts')
    parser_delete.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. id=5108bc20'
    )
    parser_delete.set_defaults(func=cli.delete)

    parser_heartbeat = subparsers.add_parser('heartbeat', help='Send heartbeat to server')
    parser_heartbeat.add_argument(
        '-T',
        '--tag',
        action='append',
        dest='tags',
        default=list(),
        help='List of tags eg. "London", "os:linux", "AWS/EC2".'
    )
    parser_heartbeat.add_argument(
        '-O',
        '--origin',
        default=None,
        help='Origin of alert or heartbeat. Usually in form of "app/host"'
    )
    parser_heartbeat.add_argument(
        '--timeout',
        default=None,
        help='Timeout in seconds before a heartbeat will be considered stale'
    )
    parser_heartbeat.set_defaults(func=cli.heartbeat)

    parser_version = subparsers.add_parser('version', help='Show alerta version info')
    parser_version.set_defaults(func=cli.version)

    args = parser.parse_args(left)

    args.output = 'json' if args.json else args.output

    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    root = logging.getLogger()

    if args.debug:
        root.setLevel(logging.DEBUG)
        LOG.setLevel(logging.DEBUG)
        LOG.debug("Alerta cli version: %s", __version__)
    else:
        root.setLevel(logging.ERROR)
        LOG.setLevel(logging.ERROR)

    cli.set_api(url=args.endpoint)

    args.func(args)


if __name__ == '__main__':
        main()
