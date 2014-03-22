
import os
import sys
import argparse
import datetime
import urlparse
import ConfigParser

from api import ApiClient
from alert import Alert
from heartbeat import Heartbeat

__version__ = '3.0.0'


DEFAULT_CONF_FILE = '~/.alerta.conf'


class AlertCommand(object):

    def __init__(self):

        self.api = None

    def set_api(self, url):

        o = urlparse.urlparse(url)
        if o.scheme == "https":
            secure = True
        else:
            secure = False
        self.api = ApiClient(host=o.hostname, port=o.port, root=o.path, secure=secure)

    def config(self, args):

        pass

    def query(self, args):

        pass

    def sender(self, args):

        if args.heartbeat:

            heartbeat = Heartbeat(
                origin=args.origin,
                tags=args.tags,
                timeout=args.timeout
            )
            print self.api.send_heartbeat(heartbeat)

        else:

            alert = Alert(

            )
            return self.api.send_alert(alert)


def main():

    cli = AlertCommand()

    defaults = {
        'profile': None,
        'api_url': 'http://api.alerta.io',
        'color': 'yes',
        'timezone': 'Europe/London',
        'output': 'text'
    }

    # ARGUMENTS
    parser = argparse.ArgumentParser(
        prog='alert',
        description="Alerta client unified command-line tool",

    )
    parser.add_argument(
        '--profile',
        default=None,
        help='profile section'
    )
    parser.add_argument(
        '--output',
        default='text',
        help='Output format of "text", "table" or "json"'
    )
    parser.add_argument(
        '--json',
        '-j',
        action='store_true',
        help='Output type JSON. Equivalent to "--output json"'
    )
    subparsers = parser.add_subparsers(metavar='COMMAND', help='query, sender or config')

    parser_query = subparsers.add_parser('config', help='Dump config of unified command-line tool')
    parser_query.set_defaults(func=cli.config)

    parser_query = subparsers.add_parser('query', help='List alerts based on query filter')
    parser_query.add_argument(
        '-i',
        '--id',
        action='append',
        dest='id',
        help='Alert ID (can use 8-char abbrev id)'
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
        '-E',
        '--environment',
        action='append',
        help='environment eg. "production", "development", "testing"'
    )
    parser_sender.add_argument(
        '-S',
        '--service',
        action='append',
        help='service affected eg. the application name, "Web", "Network", "Storage", "Database", "Security"'
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
        '--timeout',
        default=None,
        help='Timeout in seconds before an "open" alert will be automatically "expired" or "deleted"'
    )
    parser_sender.add_argument(
        '-H',
        '--heartbeat',
        action='store_true',
        default=False,
        help='Send heartbeat to server. Use in conjunction with "--origin" and "--tags"'
    )
    parser_sender.set_defaults(func=cli.sender)

    args = parser.parse_args()
    print args



    config_file = os.environ.get('ALERTA_CONF_FILE') or DEFAULT_CONF_FILE

    print 'Reading %s' % config_file
    config = ConfigParser.SafeConfigParser(defaults=defaults)
    config.read( os.path.expanduser(config_file))

    # DEFAULTS
    print config.defaults()

    # PROFILES
    print config.sections()
    for section in config.sections():
        if section.startswith('profile '):
            profile = section.replace('profile ', '')
            for option in config.options(section):
                print '[%s] %s = %s' % (profile, option, config.get(section, option))


    print defaults['api_url']


    cli.set_api(url='http://localhost:8080/api')


    args.func(args)


if __name__ == '__main__':
        main()
