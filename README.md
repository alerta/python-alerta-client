Alerta Command-Line Tool
========================

[![Build Status](https://travis-ci.org/alerta/python-alerta-client.svg?branch=master)](https://travis-ci.org/alerta/python-alerta-client) [![Gitter chat](https://badges.gitter.im/alerta/chat.png)](https://gitter.im/alerta/chat)

Unified command-line tool, terminal GUI and python SDK for the Alerta monitoring system.

![screen shot](/docs/images/alerta-top-80x25.png?raw=true&v=1)

Related projects can be found on the Alerta Org Repo at <https://github.com/alerta/>.

----

Installation
------------

To install the Alerta CLI tool run::

    $ pip install alerta

Configuration
-------------

Options can be set in a configuration file, as environment variables or on the command line.
Profiles can be used to easily switch between different configuration settings.

| Option     | Config File | Environment Variable       | Optional Argument               | Default                   |
|------------|-------------|----------------------------|---------------------------------|---------------------------|
| file       | n/a         | ``ALERTA_CONF_FILE``       | n/a                             | ``~/.alerta.conf``        |
| profile    | profile     | ``ALERTA_DEFAULT_PROFILE`` | ``--profile PROFILE``           | None                      |
| endpoint   | endpoint    | ``ALERTA_ENDPOINT``        | ``--endpoint-url URL``          | ``http://localhost:8080`` |
| key        | key         | ``ALERTA_API_KEY``         | n/a                             | None                      |
| timezone   | timezone    | n/a                        | n/a                             | Europe/London             |
| SSL verify | sslverify   | ``REQUESTS_CA_BUNDLE``     | n/a                             | verify SSL certificates   |
| timeout    | timeout     | n/a                        | n/a                             | 5s TCP connection timeout |
| output     | output      | n/a                        | ``--output OUTPUT``, ``--json`` | text                      |
| color      | color       | ``CLICOLOR``               | ``--color``, ``--no-color``     | color on                  |
| debug      | debug       | ``DEBUG``                  | ``--debug``                     | no debug                  |

Example
-------

Configuration file ``~/.alerta.conf``::

    [DEFAULT]
    timezone = Australia/Sydney
    # output = json
    profile = production

    [profile production]
    endpoint = https://api.alerta.io
    key = demo-key

    [profile development]
    endpoint = https://localhost:8443
    sslverify = off
    timeout = 10.0
    debug = yes

Environment Variables
---------------------

Set environment variables to use production configuration settings by default::

    $ export ALERTA_CONF_FILE=~/.alerta.conf
    $ export ALERTA_DEFAULT_PROFILE=production

    $ alerta query

And to switch to development configuration settings when required use the ``--profile`` option::

    $ alerta --profile development query

Usage
-----

    $ alerta --help
    usage: alerta [OPTIONS] COMMAND [FILTERS]

    Alerta client unified command-line tool

    optional arguments:
      -h, --help          show this help message and exit
      --profile PROFILE   Profile to apply from ~/.alerta.conf
      --endpoint-url URL  API endpoint URL
      --output OUTPUT     Output format of "text" or "json"
      --json, -j          Output in JSON format. Shortcut for "--output json"
      --color, --colour   Color-coded output based on severity
      --debug             Print debug output

    Commands:
      COMMAND
        send              Send alert to server
        query             List alerts based on query filter
        watch             Watch alerts based on query filter
        top               Show top offenders and stats
        raw               Show alert raw data
        history           Show alert history
        tag               Tag alerts
        untag             Remove tags from alerts
        ack               Acknowledge alerts
        unack             Unacknowledge alerts
        close             Close alerts
        delete            Delete alerts
        blackout          Blackout alerts based on attributes
        blackouts         List all blackout periods
        heartbeat         Send heartbeat to server
        heartbeats        List all heartbeats
        user              Manage user details (Basic Auth only).
        users             List all users
        key               Create API key
        keys              List all API keys
        revoke            Revoke API key
        status            Show status and metrics
        uptime            Show server uptime
        version           Show alerta version info
        help              Show this help

    Filters:
        Query parameters can be used to filter alerts by any valid alert attribute

        resource=web01     Show alerts with resource equal to "web01"
        resource!=web01    Show all alerts except those with resource of "web01"
        event=~down        Show alerts that include "down" in event name
        event!=~down       Show all alerts that don't have "down" in event name

        Special query parameters include "limit", "sort-by", "from-date" and "q" (a
        json-compliant mongo query).

Python SDK
==========

The alerta client python package can also be used as a Python SDK.

Example
-------

    >>> from alertaclient.api import ApiClient
    >>> from alertaclient.alert import Alert
    >>>
    >>> api = ApiClient(endpoint='http://api.alerta.io', key='tiPMW41QA+cVy05E7fQA/roxAAwHqZq/jznh8MOk')
    >>> alert = Alert(resource='foo', event='bar')
    >>> alert
    Alert(id='b34410b0-884f-49f9-9685-f54c2f0a449c', environment='', resource='foo', event='bar', severity='normal', status='unknown', customer=None)
    >>> api.send(alert)
    {u'status': u'error', u'message': u'[POLICY] Alert environment must be one of Production, Development'}
    >>> alert = Alert(environment='Development', resource='foo', event='bar', service=['Web'])
    >>> api.send(alert)['id']
    u'5fdb224b-9378-422d-807e-fdf8610416d2'

    >>> api.get_alert('5fdb224b-9378-422d-807e-fdf8610416d2')['alert']['severity']
    u'normal'
    >>>
    >>> api.get_alerts(query=[('resource','foo')])['alerts'][0]['id']
    u'5fdb224b-9378-422d-807e-fdf8610416d2'

    >>> from alertaclient.heartbeat import Heartbeat
    >>> hb = Heartbeat(origin='baz')
    >>> hb
    Heartbeat(id='83ecb3d6-c6cf-44eb-bdf6-1e8990b82050', origin='baz', create_time=datetime.datetime(2017, 8, 17, 21, 45, 25, 914369), timeout=300, customer=None)
    >>> api.send(hb)['status']
    u'ok'
    >>>

License
-------

Copyright (c) 2014-2017 Nick Satterly. Available under the MIT License.

