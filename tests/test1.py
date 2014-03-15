#!/usr/bin/env python

from alerta import ApiClient, Alert

client = ApiClient(host='localhost', port=9000)

r = client.query()
print r

alert = Alert(resource="foo", event="bar")
print repr(alert)

id = client.send(alert)
print id

client.ack(id)
client.tag(id, ['one','two','three'])

