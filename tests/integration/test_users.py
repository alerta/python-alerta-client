import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_user(self):
        users = self.client.get_users()
        self.assertEqual(users[0].name, 'admin@alerta.io')
        self.assertEqual(sorted(users[0].roles), sorted(['admin']))
        self.assertEqual(users[0].status, 'active')
