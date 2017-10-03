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
| output     | output      | n/a                        | ``--output OUTPUT``             | simple                    |
| color      | color       | ``CLICOLOR``               | ``--color``, ``--no-color``     | color on                  |
| debug      | debug       | ``DEBUG``                  | ``--debug``                     | no debug                  |

Example
-------

Configuration file ``~/.alerta.conf``::

    [DEFAULT]
    timezone = Australia/Sydney
    # output = psql
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

    $ alerta
    Usage: alerta [OPTIONS] COMMAND [ARGS]...
    
      Alerta client unified command-line tool.
    
    Options:
      --config-file <FILE>      Configuration file.
      --profile <PROFILE>       Configuration profile.
      --endpoint-url <URL>      API endpoint URL.
      --output-format <FORMAT>  Output format. eg. simple, grid, psql, presto, rst
      --color / --no-color      Color-coded output based on severity.
      --debug                   Debug mode.
      --help                    Show this message and exit.
    
    Commands:
      ack         acknowledge alert
      blackout    suppress alerts
      blackouts   list alert suppressions
      close       close alert
      customer    add customer lookup
      customers   list customer lookups
      delete      delete alert
      heartbeat   send a heartbeat
      heartbeats  list heartbeats
      help        show this help
      history     show alert history
      key         create API key
      keys        list API keys
      login       login with user credentials
      logout      clear local login credentials
      perm        add role-permission lookup
      perms       list role-permission lookups
      query       search for alerts
      raw         show alert raw data
      revoke      revoke API key
      send        send an alert
      status      display status and metrics
      tag         tag alert
      token       display current auth token
      unack       un-acknowledge alert
      untag       untag alert
      update      update alert attributes
      uptime      display server uptime
      user        update user
      users       list users
      version     display version info
      whoami      disply current logged in user

Python SDK
==========

The alerta client python package can also be used as a Python SDK.

Example
-------

    >>> from alertaclient.api import Client

    >>> client = Client(key='NGLxwf3f4-8LlYN4qLjVEagUPsysn0kb9fAkAs1l')
    >>> client.send_alert(environment='Production', service=['Web', 'Application'], resource='web01', event='HttpServerError', value='501', text='Web server unavailable.')
    Alert(id='42254ef8-7258-4300-aaec-a9ad7d3a84ff', environment='Production', resource='web01', event='HttpServerError', severity='normal', status='closed', customer=None)

    >>> [a.id for a in client.search([('resource','~we.*01'), ('environment!', 'Development')])]
    ['42254ef8-7258-4300-aaec-a9ad7d3a84ff']
    
    >>> client.heartbeat().serialize()['status']
    'ok'

License
-------

Copyright (c) 2014-2017 Nick Satterly. Available under the MIT License.
