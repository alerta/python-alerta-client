import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_blackout(self):
        blackout = self.client.create_blackout(
            environment='Production', service=['Web', 'App'], resource='web01', event='node_down', group='Network',
            tags=['london', 'linux'], origin='foo/bar'
        )
        blackout_id = blackout.id

        self.assertEqual(blackout.environment, 'Production')
        self.assertEqual(blackout.service, ['Web', 'App'])
        self.assertIn('london', blackout.tags)
        self.assertIn('linux', blackout.tags)
        self.assertEqual(blackout.origin, 'foo/bar')

        blackout = self.client.update_blackout(blackout_id, environment='Development', group='Network',
                                               origin='foo/quux', text='updated blackout')
        self.assertEqual(blackout.environment, 'Development')
        self.assertEqual(blackout.group, 'Network')
        self.assertEqual(blackout.origin, 'foo/quux')
        self.assertEqual(blackout.text, 'updated blackout')

        blackout = self.client.create_blackout(
            environment='Production', service=['Core'], group='Network', origin='foo/baz'
        )

        blackouts = self.client.get_blackouts()
        self.assertEqual(len(blackouts), 2)

        self.client.delete_blackout(blackout_id)

        blackouts = self.client.get_blackouts()
        self.assertEqual(len(blackouts), 1)
