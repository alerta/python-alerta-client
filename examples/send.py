#!/usr/bin/env python

from alertaclient.api import AlertaClient
from alertaclient.models.alert import Alert

client = AlertaClient()

alert = Alert(
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

try:
    print(client.send(alert))
except Exception as e:
    print(e)
