import unittest

import requests_mock

from alertaclient.api import Client


class PermissionTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.perm = """
            {
              "id": "584f38f4-b44e-4d87-9b61-c106d21bcc7a",
              "permission": {
                "href": "http://localhost:8080/perm/584f38f4-b44e-4d87-9b61-c106d21bcc7a",
                "id": "584f38f4-b44e-4d87-9b61-c106d21bcc7a",
                "match": "websys",
                "scopes": [
                  "admin:users",
                  "admin:keys",
                  "write"
                ]
              },
              "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_permission(self, m):
        m.post('http://localhost:8080/perm', text=self.perm)
        perm = self.client.create_perm(role='websys', scopes=['admin:users', 'admin:keys', 'write'])
        self.assertEqual(perm.match, 'websys')
        self.assertEqual(sorted(perm.scopes), sorted(['admin:users', 'admin:keys', 'write']))
