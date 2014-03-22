
import os
import sys
import argparse
import datetime
import ConfigParser

__version__ = '3.0.0'


DEFAULT_CONF_FILE = '~/.alerta.conf'


class AlertCommand(object):

    def config(self, args):

        pass

    def query(self, args):

        pass

    def sender(self, args):

        pass


def main():

    cli = AlertCommand()

    defaults = {
        'profile': None,
        'api_url': 'http://api.alerta.io',
        'color': 'yes',
        'timezone': 'Europe/London',
        'output': 'text'
    }

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
        '-t',
        '--text',
        help='Freeform alert text eg. "Host not responding to ping."'
    )
    parser_sender.add_argument(
        'filter',
        nargs='*',
        metavar='KEY=VALUE',
        help='eg. prority=high service=Network'
    )
    parser_sender.set_defaults(func=cli.sender)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
        main()
