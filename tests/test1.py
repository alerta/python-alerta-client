#!/usr/bin/env python

from alerta import ApiClient, Alert

client = ApiClient(host='localhost', port=9000)

print ApiClient.__mro__

r = client.get_alerts(service="web")
print r

alert = Alert(resource="foo", event="bar")
print repr(alert)

response = client.send_alert(alert)
print response
id = response['receivedAlert']['_id']
print id

print client.ack_alert(id)
print client.tag_alert(id, ['one', 'two', 'three'])

