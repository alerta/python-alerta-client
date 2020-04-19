import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_permission(self):
        perm = self.client.create_perm(role='websys', scopes=['admin:users', 'admin:keys', 'write'])
        self.assertEqual(perm.match, 'websys')
        self.assertEqual(sorted(perm.scopes), sorted(['admin:users', 'admin:keys', 'write']))
