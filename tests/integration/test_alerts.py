import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_alert(self):
        id, alert, message = self.client.send_alert(
            environment='Production', resource='web01', event='node_down', correlated=['node_up', 'node_down'],
            service=['Web', 'App'], severity='critical', tags=['london', 'linux'], value=4
        )
        self.assertEqual(alert.value, '4')  # values cast to string
        self.assertEqual(alert.timeout, 86400)  # timeout returned as int
        self.assertIn('london', alert.tags)

    def test_alert_notes(self):
        alert_id, alert, message = self.client.send_alert(
            environment='Production', resource='web02', event='node_down', correlated=['node_up', 'node_down'],
            service=['Web', 'App'], severity='critical', tags=['london', 'linux'], value=4
        )
        note = self.client.alert_note(alert_id, text='this is a test note')
        self.assertEqual(note.text, 'this is a test note')

        notes = self.client.get_alert_notes(alert_id)
        self.assertEqual(notes[0].text, 'this is a test note')
        self.assertEqual(notes[0].user, 'admin@alerta.io')

        note = self.client.update_alert_note(alert_id, notes[0].id, text='updated note text')
        self.assertEqual(note.text, 'updated note text')

        self.client.delete_alert_note(alert_id, notes[0].id)

        notes = self.client.get_alert_notes(alert_id)
        self.assertEqual(notes, [])
