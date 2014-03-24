#!/usr/bin/env python

from alerta.client import Alert, ApiClient

client = ApiClient()

alert = Alert(resource='res1', event='event1')
print alert

print client.send(alert)
