import unittest

import requests_mock

from alertaclient.api import Client


class ApiKeyTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.key = """
            {
              "data": {
                "count": 0,
                "customer": null,
                "expireTime": "2018-10-03T08:36:14.651Z",
                "href": "http://localhost:8080/key/BpSG0Ck5JCqk5TJiuBSLAWuTs03QKc_527T5cDtw",
                "id": "f4203347-d1b2-4f56-b5e9-6de97cf2d8ae",
                "key": "BpSG0Ck5JCqk5TJiuBSLAWuTs03QKc_527T5cDtw",
                "lastUsedTime": null,
                "scopes": [
                  "write:alerts",
                  "admin:keys"
                ],
                "text": "Ops kAPI Key",
                "type": "read-write",
                "user": "johndoe@example.com"
              },
              "key": "BpSG0Ck5JCqk5TJiuBSLAWuTs03QKc_527T5cDtw",
              "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_key(self, m):
        m.post('http://localhost:8080/key', text=self.key)
        api_key = self.client.create_key(username='johndoe@example.com', scopes=[
                                         'write:alerts', 'admin:keys'], text='Ops API Key')
        self.assertEqual(api_key.user, 'johndoe@example.com')
        self.assertEqual(sorted(api_key.scopes), sorted(['write:alerts', 'admin:keys']))
