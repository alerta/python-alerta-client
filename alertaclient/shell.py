
import os
import sys
import argparse
import time
import pytz
import datetime
import ConfigParser
import json
import prettytable

from api import ApiClient
from alert import Alert
from heartbeat import Heartbeat

__version__ = '3.0.0'

DEFAULT_CONF_FILE = '~/.alerta.conf'
DEFAULT_ENDPOINT_URL = 'prog://system'
DEFAULT_OUTPUT = 'text'
DEFAULT_TIMEZONE = 'Europe/London'


class AlertCommand(object):

    def __init__(self):

        self.api = None

    def set_api(self, url):

        self.api = ApiClient(endpoint=url)

    def config(self, args):

        print args

    def query(self, args):

        now = datetime.datetime.utcnow()
        from_time = now

        query = dict([x.split('=', 1) for x in args.filter if '=' in x])

        while True:
            try:
                response = self.api.get_alerts(**query)
            except Exception as e:
                print >>sys.stderr, "ERROR: %s" % e
                sys.exit(1)

            if response['status'] == "error":
                print >>sys.stderr, "ERROR: %s" % response['message']
                sys.exit(1)
            else:
                alerts = response['alerts']
                if args.output == "json":
                    dump_alerts(alerts)
                elif args.output == "text":
                    show_alerts(alerts, args)
                elif args.output == "table":
                    table_alerts(alerts)
                else:
                    print >>sys.stderr, "ERROR: Unknown output format"
                    sys.exit(1)

            if args.watch:
                try:
                    time.sleep(2)
                except (KeyboardInterrupt, SystemExit):
                    sys.exit(0)
                query['from-date'] = response['lastTime']
            else:
                break

    def sender(self, args):

        if args.heartbeat:
            try:
                heartbeat = Heartbeat(
                    origin=args.origin,
                    tags=args.tags,
                    timeout=args.timeout
                )
            except Exception as e:
                print >>sys.stderr, "ERROR: %s" % e
                sys.exit(1)

            try:
                response = self.api.send(heartbeat)
            except Exception as e:
                print >>sys.stderr, "ERROR: %s" % e
            else:
                print response

        else:
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
                    # create_time=args.create_time,
                    timeout=args.timeout,
                    raw_data=args.raw_data
                )
            except Exception as e:
                print >>sys.stderr, "ERROR: %s" % e
                sys.exit(1)

            try:
                response = self.api.send(alert)
            except Exception as e:
                print >>sys.stderr, "ERROR: %s" % e
            else:
                print response


def dump_alerts(alerts):

    print json.dumps(alerts, indent=4)


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


def show_alerts(alerts, args):

    tz = pytz.timezone(args.timezone)

    if args.color:
        end_color = _ENDC

    for alert in alerts:
        line_color = ''
        end_color = ''

        last_receive_time = datetime.datetime.strptime(alert.get('lastReceiveTime', None), '%Y-%m-%dT%H:%M:%S.%fZ')
        last_receive_time = last_receive_time.replace(tzinfo=pytz.utc)

        if args.color:
            line_color = _COLOR_MAP[alert['severity']]
        print(line_color + '%s|%s|%s|%5d|%-5s|%-10s|%-18s|%12s|%16s|%12s' % (
            alert['id'][0:8],
            last_receive_time.astimezone(tz).strftime('%Y/%m/%d %H:%M:%S'),
            alert['severity'],
            alert['duplicateCount'],
            alert.get('environment', NOT_SET),
            ','.join(alert.get('service', NOT_SET)),
            alert['resource'],
            alert.get('group', NOT_SET),
            alert['event'],
            alert.get('value', NOT_SET) + end_color))


def table_alerts(alerts):

    pt = prettytable.PrettyTable([
        "Alert ID",
        "Last Receive Time",
        "Severity",
        "Dupl.",
        "Environment",
        "Service",
        "Resource",
        "Group",
        "Event",
        "Value"
    ])
    col_text = []
    for alert in alerts:
            pt.add_row([
                alert['id'],
                alert['lastReceiveTime'],
                alert['severity'],
                alert['duplicateCount'],
                alert.get('environment', NOT_SET),
                ','.join(alert.get('service', '')),
                alert['resource'],
                alert.get('group', NOT_SET),
                alert['event'],
                alert.get('value', NOT_SET)
            ])
        # if 'text' in CONF.show:
        #     col_text.append(text)
            print pt


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
        help='Define profile section to use in configuration file %s' % defaults['config_file']
    )
    args, left = profile_parser.parse_known_args()

    # print 'defaults before reading in config -> %s' % defaults
    config_file = defaults['config_file']

    if config_file:

        # print 'Reading %s...' % config_file

        config = ConfigParser.SafeConfigParser(defaults=defaults)
        config.read(os.path.expanduser(config_file))

        defaults = dict(config.defaults())

        # print 'defaults after reading in config -> %s' % defaults

        if args.profile:
            defaults['profile'] = args.profile
            # PROFILES
            for section in config.sections():
                # print 'Found -> %s' % section
                if section.startswith('profile '):
                    # print 'Reading -> %s' % section
                    if args.profile == section.replace('profile ', ''):
                        # print '*** Matched %s' % args.profile
                        defaults['debug'] = config.getboolean(section, 'debug')
                        defaults['endpoint'] = config.get(section, 'endpoint')
                        defaults['output'] = config.get(section, 'output')
                        defaults['color'] = config.getboolean(section, 'color')
                        defaults['timezone'] = config.get(section, 'timezone')

    parser = argparse.ArgumentParser(
        prog='alert',
        description="Alerta client unified command-line tool",
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
        '--version',
        action='version',
        version='%(prog)s cli v' + __version__,
        help='version'
    )
    parser.add_argument(
        '--color',
        '--colour',
        action='store_true',
        default=defaults['color'],
        help='color'
    )
    parser.add_argument(
        '--no-color',
        '--no-colour',
        action='store_false',
        default=defaults['color'],
        dest='color',
        help=argparse.SUPPRESS
    )
    subparsers = parser.add_subparsers(metavar='COMMAND', help='query, sender or config')

    parser_query = subparsers.add_parser('config', help='Dump config of unified command-line tool')
    parser_query.set_defaults(func=cli.config)

    parser_query = subparsers.add_parser('query', help='List alerts based on query filter')
    parser_query.add_argument(
        '--show',
        help='Show '
    )
    parser_query.add_argument(
        '-w',
        '--watch',
        action='store_true',
        help='Periodically poll for new  alerts every 2 seconds'
    )
    parser_query.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. stack=soulmates'
    )
    parser_query.set_defaults(func=cli.query)

    parser_sender = subparsers.add_parser('sender', help='Send alert to server')
    parser_sender.add_argument(
        '-r',
        '--resource',
        help='resource under alarm'
    )
    parser_sender.add_argument(
        '-e',
        '--event',
        help='event'
    )
    parser_sender.add_argument(
        '-E',
        '--environment',
        action='append',
        help='environment eg. "production", "development", "testing"'
    )
    parser_sender.add_argument(
        '-s',
        '--severity',
        help='severity'
    )
    parser_sender.add_argument(
        '-C',
        '--correlate',
        action='append',
        help='correlate'
    )
    parser_sender.add_argument(
        '--status',
        help='status should not normally be defined eg. "open", "closed"'
    )
    parser_sender.add_argument(
        '-S',
        '--service',
        action='append',
        help='service affected eg. the application name, "Web", "Network", "Storage", "Database", "Security"'
    )
    parser_sender.add_argument(
        '-g',
        '--group',
        help='group'
    )
    parser_sender.add_argument(
        '-v',
        '--value',
        help='value'
    )
    parser_sender.add_argument(
        '-t',
        '--text',
        help='Freeform alert text eg. "Host not responding to ping."'
    )
    parser_sender.add_argument(
        '-T',
        '--tag',
        action='append',
        dest='tags',
        default=list(),
        help='List of tags eg. "London", "os:linux", "AWS/EC2".'
    )
    parser_sender.add_argument(
        '-A',
        '--attribute',
        action='append',
        dest='attributes',
        default=list(),
        help='List of Key=Value attribute pairs eg. "priority=high", "moreInfo=..."'
    )
    parser_sender.add_argument(
        '-O',
        '--origin',
        default=None,
        help='Origin of alert or heartbeat. Usually in form of "app/host"'
    )
    parser_sender.add_argument(
        '--type',
        dest='event_type',
        default='exceptionAlert',
        help='event type eg. "exceptionAlert", "serviceAlert"'
    )
    parser_sender.add_argument(
        '-H',
        '--heartbeat',
        action='store_true',
        default=False,
        help='Send heartbeat to server. Use in conjunction with "--origin" and "--tags"'
    )
    parser_sender.add_argument(
        '--timeout',
        default=None,
        help='Timeout in seconds before an "open" alert will be automatically "expired" or "deleted"'
    )
    parser_sender.add_argument(
        '--raw-data',
        default=None,
        help='raw data'
    )
    parser_sender.set_defaults(func=cli.sender)

    args = parser.parse_args(left)

    args.output = 'json' if args.json else args.output
    # print 'ARGS > %s' % args



    # print defaults['endpoint']
    #
    # print 'config_file => %s' % defaults['config_file']
    # print 'profile  => %s' % args.profile
    # print 'endpoint => %s' % args.endpoint
    # print 'output   => %s' % args.output
    # print 'color    => %s' % args.color
    # print 'debug    => %s' % args.debug
    # print 'timezone => %s' % args.timezone

    cli.set_api(url='http://localhost:8080/api')

    args.func(args)


if __name__ == '__main__':
        main()
