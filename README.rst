
Introduction
============

Alerta is a monitoring tool that allows alerts from many different systems to be consolidated into a single view.

Currently there are integrations for tools that support standard protocols such as ``SNMP``, ``syslog`` and ``HTTP``.
There are also specific integrations for popular monitoiring tools such as Nagios_, Zabbix_ and Riemann_.

.. _`nagios`: https://github.com/alerta/nagios3-alerta
.. _`zabbix`: https://github.com/alerta/zabbix-alerta
.. _`riemann`: https://github.com/guardian/riemann-config/blob/master/alerta.clj


Installation
============

Installing this package makes available an API that can be used to send alerts to the alerta system and
to query the alert database::

    $ pip install alerta


Configuration
=============

For a basic configuration that can be used to test the client tools against a demo alerta server, use::

    [DEFAULT]
    timezone = Europe/London
    api_host = api.alerta.io
    api_port = 80

    [alert-query]
    colour = yes

Copy this configuration to ``/etc/alerta/alerta.conf`` or ``$HOME/.alerta.conf`` files::

    $ mv /path/to/alerta.conf.sample $HOME/.alerta.conf

or use the ``ALERTA_CONF`` environment variable::

    $ export ALERTA_CONF=/path/to/alerta.conf


Python API
==========

A python API can be used to generate alerts::

    >>> from alerta.common.api import ApiClient
    >>> from alerta.common.alert import Alert
    >>>
    >>> client = ApiClient(host='api.alerta.io', port=80)
    >>> alert = Alert(resource="foo", event="bar")
    >>>
    >>> client.send(alert)
    u'8e9c4736-c2a8-4b4d-8638-07dad6ed1d2b'
    >>>

The python API can also be used to query for alerts::

    >>> from alerta.common.api import ApiClient
    >>>
    >>> client = ApiClient(host='api.alerta.io', port=80)
    >>> r = client.query()
    >>> r['status']
    u'ok'
    >>> pp = pprint.PrettyPrinter(indent=4)
    >>> pp.pprint(r['alerts']['severityCounts'])
    {   u'cleared': 0,
        u'critical': 1,
        u'debug': 0,
        u'indeterminate': 0,
        u'informational': 0,
        u'major': 2,
        u'minor': 1,
        u'normal': 4,
        u'security': 0,
        u'unknown': 0,
        u'warning': 1}
