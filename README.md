Alerta Command-Line Tool
========================

Unified command-line tool and python API for [alerta](https://github.com/guardian/alerta).


Installation
------------

    $ pip install alerta


Configuration
-------------

ALERTA_CONF_FILE=
ALERTA_DEFAULT_URL=
ALERTA_DEFAULT_PROFILE=production
ALERTA_DEFAULT_OUTPUT=text

0. set defaults
1. read in env vars
2. use CONF_FILE env var to read in config file
3. use DEF_PROFILE env var to get settings
4. override defaults with DEFAULTs if no profile
5. override settings with command-line options

ENV VAR
ALERTA_CONF_FILE
ALERTA_DEFAULT_PROFILE
ALERTA_DEFAULT_ENDPOINT
CLICOLOR

ConfigFile
[profile development]
debug = yes
endpoint = http://sldfja
output = json
color = yes
timezone = Australia/Sydney

Options
--debug
--endpoint-url
--output
--json
--profile
--color


Python SDK
==========

The python packages used by the client command-line tool can also be used as a Python SDK.


Example
-------

    >>> from alerta.api import ApiClient
    >>> from alerta.alert import Alert
    >>>
    >>> api = ApiClient(endpoint='http://api.alerta.io', key='tiPMW41QA+cVy05E7fQA/roxAAwHqZq/jznh8MOk')
    >>> alert = Alert(resource='foo', event='bar')
    >>> alert
    Alert(id='6e625266-fb7c-4c11-bf95-27a6a0be432b', environment='', resource='foo', event='bar', severity='normal', status='unknown')
    >>> api.send(alert)
    {u'status': u'ok', u'id': u'5fdb224b-9378-422d-807e-fdf8610416d2'}

    >>> api.get_alert('5fdb224b-9378-422d-807e-fdf8610416d2')['alert']['severity']
    u'normal'
    >>>
    >>> api.get_alerts(resource='foo')['alerts'][0]['id']
    u'5fdb224b-9378-422d-807e-fdf8610416d2'

    >>> from alerta.heartbeat import Heartbeat
    >>> hb = Heartbeat(origin='baz')
    >>> hb
    Heartbeat(id='21d586a6-9bd5-4b18-b0bb-4fb876db4851', origin='baz', create_time=datetime.datetime(2014, 6, 14, 20, 2, 33, 55118), timeout=300)
    >>> api.send(hb)
    {u'status': u'ok', u'id': u'6bf11e97-9664-4fa3-b830-8e6d0d84b4cc'}
    >>>

License
-------

Copyright (c) 2014 Nick Satterly. Available under the MIT License.

