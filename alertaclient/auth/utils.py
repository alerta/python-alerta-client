
import os
from netrc import netrc
from urllib.parse import urlparse

import click

NETRC_FILE = os.path.join(os.environ['HOME'], '.netrc')


def machine(endpoint):
    u = urlparse(endpoint)
    return '{}:{}'.format(u.hostname, u.port or '80')


def get_token(endpoint):
    try:
        info = netrc(NETRC_FILE)
    except Exception:
        return
    auth = info.authenticators(machine(endpoint))
    if auth is not None:
        _, _, password = auth
        return password


def save_token(endpoint, username, token):
    with open(NETRC_FILE, 'a'):  # touch file
        pass
    try:
        info = netrc(NETRC_FILE)
    except Exception as e:
        raise click.UsageError('{}'.format(e))
    info.hosts[machine(endpoint)] = (username, None, token)
    with open(NETRC_FILE, 'w') as f:
        f.write(dump_netrc(info))


def clear_token(endpoint):
    try:
        info = netrc(NETRC_FILE)
    except Exception as e:
        raise click.UsageError('{}'.format(e))
    try:
        del info.hosts[machine(endpoint)]
        with open(NETRC_FILE, 'w') as f:
            f.write(dump_netrc(info))
    except KeyError as e:
        raise click.UsageError('No credentials stored for {}'.format(e))


# See https://bugs.python.org/issue30806
def dump_netrc(self):
    """Dump the class data in the format of a .netrc file."""
    rep = ''
    for host in self.hosts.keys():
        attrs = self.hosts[host]
        rep = rep + 'machine ' + host + '\n\tlogin ' + str(attrs[0]) + '\n'
        if attrs[1]:
            rep = rep + 'account ' + str(attrs[1])
        rep = rep + '\tpassword ' + str(attrs[2]) + '\n'
    for macro in self.macros.keys():
        rep = rep + 'macdef ' + macro + '\n'
        for line in self.macros[macro]:
            rep = rep + line
        rep = rep + '\n'
    return rep
