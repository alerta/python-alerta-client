#!/usr/bin/env python

from alerta import ApiClient, Alert

client = ApiClient(host='localhost', port=9000)
alert = Alert(resource="foo", event="bar")

print repr(alert)

id = client.send(alert)
print id
