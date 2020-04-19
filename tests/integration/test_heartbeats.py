import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_heartbeat(self):
        hb = self.client.heartbeat(origin='app/web01', timeout=10, tags=['london', 'linux'])
        self.assertEqual(hb.origin, 'app/web01')
        self.assertEqual(hb.event_type, 'Heartbeat')
        self.assertEqual(hb.timeout, 10)
        self.assertIn('linux', hb.tags)
