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

    def test_blackout(self):
        blackout = self.client.create_blackout(
            environment='Production', service=['Web', 'App'], resource='web01', event='node_down', group='Network', tags=['london', 'linux']
        )
        self.assertEqual(blackout.environment, 'Production')
        self.assertEqual(blackout.service, ['Web', 'App'])
        self.assertIn('london', blackout.tags)
        self.assertIn('linux', blackout.tags)

    def test_customer(self):
        customer = self.client.create_customer(customer='ACME Corp.', match='example.com')
        self.assertEqual(customer.customer, 'ACME Corp.')
        self.assertEqual(customer.match, 'example.com')

    def test_group(self):
        group = self.client.create_group(name='myGroup', text='test group')
        self.assertEqual(group.name, 'myGroup')
        self.assertEqual(group.text, 'test group')

    def test_heartbeat(self):
        hb = self.client.heartbeat(origin='app/web01', timeout=10, tags=['london', 'linux'])
        self.assertEqual(hb.origin, 'app/web01')
        self.assertEqual(hb.event_type, 'Heartbeat')
        self.assertEqual(hb.timeout, 10)
        self.assertIn('linux', hb.tags)

    def test_history(self):
        hist = self.client.get_history()
        self.assertEqual(hist[0].environment, 'Production')
        self.assertEqual(hist[0].service, ['Web', 'App'])
        self.assertEqual(hist[0].resource, 'web01')
        self.assertIn('london', hist[0].tags)
        self.assertEqual(hist[0].change_type, 'new')

    def test_key(self):
        api_key = self.client.create_key(
            username='johndoe@example.com', scopes=['write:alerts', 'admin:keys'], text='Ops API Key'
        )
        self.assertEqual(api_key.user, 'johndoe@example.com')
        self.assertEqual(sorted(api_key.scopes), sorted(['write:alerts', 'admin:keys']))

    def test_note(self):
        id, alert, message = self.client.send_alert(
            environment='Production', resource='web02', event='node_down', correlated=['node_up', 'node_down'],
            service=['Web', 'App'], severity='critical', tags=['london', 'linux'], value=4
        )
        note = self.client.alert_note(id, text='this is a test note')
        self.assertEqual(note.text, 'this is a test note')

        notes = self.client.get_alert_notes(id)
        self.assertEqual(notes[0].text, 'this is a test note')
        self.assertEqual(notes[0].user, 'admin@alerta.io')

        note = self.client.update_alert_note(id, notes[0].id, text='updated note text')
        self.assertEqual(note.text, 'updated note text')

        self.client.delete_alert_note(id, notes[0].id)

        notes = self.client.get_alert_notes(id)
        self.assertEqual(notes, [])

    def test_permission(self):
        perm = self.client.create_perm(role='websys', scopes=['admin:users', 'admin:keys', 'write'])
        self.assertEqual(perm.match, 'websys')
        self.assertEqual(sorted(perm.scopes), sorted(['admin:users', 'admin:keys', 'write']))

    def test_user(self):
        users = self.client.get_users()
        self.assertEqual(users[0].name, 'admin@alerta.io')
        self.assertEqual(sorted(users[0].roles), sorted(['admin']))
        self.assertEqual(users[0].status, 'active')
