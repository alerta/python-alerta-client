
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
    endpoint = http://alerta.prod.com:8080/api
    debug = no

    [profile development]
    endpoint = http://alerta.dev.com:8080/api
    debug = yes

Copy this configuration ``$HOME/.alerta.conf`` files::

    $ mv /path/to/alerta.conf.sample $HOME/.alerta.conf

or use the ``ALERTA_CONF`` environment variable::

    $ export ALERTA_CONF=/path/to/alerta.conf

