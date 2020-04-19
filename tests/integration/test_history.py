import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_alert(self):
        id, alert, message = self.client.send_alert(
            environment='Production', resource='net03', event='node_down', correlated=['node_up', 'node_down', 'node_marginal'],
            service=['Network', 'Core'], severity='critical', tags=['newyork', 'linux'], value=4
        )
        id, alert, message = self.client.send_alert(
            environment='Production', resource='net03', event='node_marginal', correlated=['node_up', 'node_down', 'node_marginal'],
            service=['Network', 'Core'], severity='minor', tags=['newyork', 'linux'], value=1
        )
        self.assertEqual(alert.value, '1')  # values cast to string
        self.assertEqual(alert.timeout, 86400)  # timeout returned as int
        self.assertIn('newyork', alert.tags)

    def test_history(self):
        hist = self.client.get_history(query=[('resource', 'net03')])
        self.assertEqual(hist[0].environment, 'Production')
        self.assertEqual(hist[0].service, ['Network', 'Core'])
        self.assertEqual(hist[0].resource, 'net03')
        self.assertIn('newyork', hist[0].tags)
        self.assertEqual(hist[0].change_type, 'new')

        self.assertEqual(hist[1].environment, 'Production')
        self.assertEqual(hist[1].service, ['Network', 'Core'])
        self.assertEqual(hist[1].resource, 'net03')
        self.assertIn('newyork', hist[1].tags)
        self.assertEqual(hist[1].change_type, 'new')
