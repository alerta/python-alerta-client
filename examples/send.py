#!/usr/bin/env python

from alerta.api import ApiClient
from alerta.alert import Alert

api = ApiClient(endpoint='http://localhost:8080', key='tUA6oBX6E5hUUQZ+dyze6vZbOMmiZWA7ke88Nvio')

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
print alert

try:
    print api.send(alert)
except Exception as e:
    print e