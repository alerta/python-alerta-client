#!/usr/bin/env python

from alertaclient.api import Client

client = Client()

try:
    id, alert, message = client.send_alert(
        resource='web-server-01',
        event='HttpError',
        correlate=['HttpOK'],
        group='Web',
        environment='Production',
        service=['theguardian.com'],
        severity='major',
        value='Bad Gateway (502)',
        text='Web server error.',
        tags=['web', 'dc1', 'london'],
        attributes={'customer': 'The Guardian'}
    )
    print(alert)
except Exception as e:
    print(e)
