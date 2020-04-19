import unittest

from alertaclient.api import Client
from alertaclient.models.enums import Scope


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_key(self):
        api_key = self.client.create_key(
            username='key@alerta.io', scopes=[Scope.write_alerts, Scope.admin_keys], text='Ops API Key'
        )
        api_key_id = api_key.id

        self.assertEqual(api_key.user, 'key@alerta.io')
        self.assertEqual(sorted(api_key.scopes), sorted(['write:alerts', 'admin:keys']))

        api_key = self.client.update_key(api_key_id, scopes=[Scope.write_alerts, Scope.write_heartbeats, Scope.admin_keys], text='Updated Ops API Key')
        self.assertEqual(sorted(api_key.scopes), sorted([Scope.write_alerts, Scope.write_heartbeats, Scope.admin_keys]))
        self.assertEqual(api_key.text, 'Updated Ops API Key')

        api_key = self.client.create_key(
            username='key@alerta.io', scopes=[Scope.admin], text='Admin API Key'
        )

        api_keys = self.client.get_keys(query=[('user', 'key@alerta.io')])
        self.assertEqual(len(api_keys), 2)

        api_keys = self.client.delete_key(api_key_id)
        self.assertEqual(len(api_keys), 1)
