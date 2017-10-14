
import os
import click

from netrc import netrc

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

NETRC_FILE = os.path.join(os.environ['HOME'], ".netrc")


def machine(endpoint):
    u = urlparse(endpoint)
    return '{}:{}'.format(u.hostname, u.port or '80')


def get_token(endpoint):
    try:
        info = netrc(NETRC_FILE)
    except OSError:
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
    except OSError:
        raise click.UsageError('Could not write to {}'.format(NETRC_FILE))
    info.hosts[machine(endpoint)] = (username, None, token)
    with open(NETRC_FILE, 'w') as f:
        f.write(dump_netrc(info))


def clear_token(endpoint):
    try:
        info = netrc(NETRC_FILE)
    except OSError:
        raise click.UsageError('No {} file.'.format(NETRC_FILE))
    try:
        del info.hosts[machine(endpoint)]
        with open(NETRC_FILE, 'w') as f:
            f.write(dump_netrc(info))
    except KeyError as e:
        raise click.UsageError('User not logged in.')


# See https://bugs.python.org/issue30806
def dump_netrc(self):
    """Dump the class data in the format of a .netrc file."""
    rep = ""
    for host in self.hosts.keys():
        attrs = self.hosts[host]
        rep = rep + "machine "+ host + "\n\tlogin " + str(attrs[0]) + "\n"
        if attrs[1]:
            rep = rep + "account " + str(attrs[1])
        rep = rep + "\tpassword " + str(attrs[2]) + "\n"
    for macro in self.macros.keys():
        rep = rep + "macdef " + macro + "\n"
        for line in self.macros[macro]:
            rep = rep + line
        rep = rep + "\n"
    return rep
