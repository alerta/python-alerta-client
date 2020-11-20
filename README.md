Alerta Command-Line Tool
========================

[![Actions Status](https://github.com/alerta/python-alerta-client/workflows/CI%20Tests/badge.svg)](https://github.com/alerta/python-alerta-client/actions)
 [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev) [![Coverage Status](https://coveralls.io/repos/github/alerta/python-alerta-client/badge.svg?branch=master)](https://coveralls.io/github/alerta/python-alerta-client?branch=master)

Unified command-line tool, terminal GUI and python SDK for the Alerta monitoring system.

![screen shot](/docs/images/alerta-top-80x25.png?raw=true&v=1)

Related projects can be found on the Alerta Org Repo at <https://github.com/alerta/>.

Installation
------------

To install the Alerta CLI tool run::

    $ pip install alerta

Configuration
-------------

Options can be set in a configuration file, as environment variables or on the command line.
Profiles can be used to easily switch between different configuration settings.

| Option            | Config File | Environment Variable       | Optional Argument               | Default                   |
|-------------------|-------------|----------------------------|---------------------------------|---------------------------|
| file              | n/a         | ``ALERTA_CONF_FILE``       | n/a                             | ``~/.alerta.conf``        |
| profile           | profile     | ``ALERTA_DEFAULT_PROFILE`` | ``--profile PROFILE``           | None                      |
| endpoint          | endpoint    | ``ALERTA_ENDPOINT``        | ``--endpoint-url URL``          | ``http://localhost:8080`` |
| key               | key         | ``ALERTA_API_KEY``         | n/a                             | None                      |
| timezone          | timezone    | n/a                        | n/a                             | Europe/London             |
| SSL verify        | sslverify   | ``REQUESTS_CA_BUNDLE``     | n/a                             | verify SSL certificates   |
| SSL client cert   | sslcert     | n/a                        | n/a                             | None                      |
| SSL client key    | sslkey      | n/a                        | n/a                             | None                      |
| timeout           | timeout     | n/a                        | n/a                             | 5s TCP connection timeout |
| output            | output      | n/a                        | ``--output-format OUTPUT``      | simple                    |
| color             | color       | ``CLICOLOR``               | ``--color``, ``--no-color``     | color on                  |
| debug             | debug       | ``DEBUG``                  | ``--debug``                     | no debug                  |

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
      ack         Acknowledge alerts
      blackout    Suppress alerts
      blackouts   List alert suppressions
      close       Close alerts
      customer    Add customer lookup
      customers   List customer lookups
      delete      Delete alerts
      heartbeat   Send a heartbeat
      heartbeats  List heartbeats
      help        Show this help
      history     Show alert history
      key         Create API key
      keys        List API keys
      login       Login with user credentials
      logout      Clear login credentials
      perm        Add role-permission lookup
      perms       List role-permission lookups
      query       Search for alerts
      raw         Show alert raw data
      revoke      Revoke API key
      send        Send an alert
      status      Display status and metrics
      tag         Tag alerts
      token       Display current auth token
      unack       Un-acknowledge alerts
      untag       Untag alerts
      update      Update alert attributes
      uptime      Display server uptime
      user        Update user
      users       List users
      version     Display version info
      whoami      Display current logged in user

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

    Alerta monitoring system and console
    Copyright 2012-2020 Nick Satterly

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
