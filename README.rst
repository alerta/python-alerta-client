
Introduction
============

Alerta is a monitoring tool that allows alerts from many different systems to be consolidated into a single view.

Currently there are integrations for tools that support standard protocols such as ``SNMP``, ``syslog`` and ``HTTP``.
There are also specific integrations for popular monitoiring tools such as Nagios_, Zabbix_, Sensu_ and Riemann_.

.. _`nagios`: https://github.com/alerta/nagios3-alerta
.. _`zabbix`: https://github.com/alerta/zabbix-alerta
.. _`sensu`: https://github.com/alerta/sensu-alerta
.. _`riemann`: https://github.com/guardian/riemann-config/blob/master/alerta.clj


Installation
============

Installing this package makes available a command-line tool that can be used to send alerts to the alerta system and
to query the alert database::

    $ pip install alerta-client


Configuration
=============

Configuration supports profiles for different environments like `production` and `development` or `testing`.

For a basic configuration that can be used to test the client tools against a demo alerta server, use::

    [DEFAULT]
    timezone = Europe/London

    [profile production]
    endpoint = http://alerta.prod.com:8080
    debug = no

    [profile development]
    endpoint = http://alerta.dev.com:8080
    debug = yes

Copy this configuration ``$HOME/.alerta.conf`` files::

    $ mv /path/to/alerta.conf.sample $HOME/.alerta.conf

or use the ``ALERTA_CONF`` environment variable::

    $ export ALERTA_CONF=/path/to/alerta.conf


Usage
=====
::

    $ alert help
    usage: alert [OPTIONS] COMMAND [FILTERS]

    Alerta client unified command-line tool

    optional arguments:
      -h, --help            show this help message and exit
      --profile PROFILE     Select profile to apply from ~/.alerta.conf
      --endpoint-url URL    API endpoint URL
      --output OUTPUT       Output format of "text" or "json"
      --json, -j            Output in JSON format. Shortcut for "--output json"
      --color, --colour     Color-coded output based on severity
      --debug               Print debug output

    Commands:
        send                Send alert to server
        query               List alerts based on query filter
        watch               Watch alerts based on query filter
        raw                 Show alert raw data
        history             Show alert history
        tag                 Tag alerts
        ack                 Acknowledge alerts
        unack               Unacknowledge alerts
        close               Close alerts
        delete              Delete alerts
        heartbeat           Send heartbeat to server
        help                Show help
        version             Show alerta version info

    Filters:
        Query parameters can be used to filter alerts by any valid alert attribute

        resource=web01     Show alerts with resource equal to "web01"
        resource!=web01    Show all alerts except those with resource of "web01"
        event=~down        Show alerts that include "down" in event name
        event!=~down       Show all alerts that don't have "down" in event name

        Special query parameters include "limit", "sort-by", "from-date" and "q" (a
        json-compliant mongo query).


Examples
========

::