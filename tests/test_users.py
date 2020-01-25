import unittest

import requests_mock

from alertaclient.api import Client


class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.user = """
            {
              "domains": [
                "alerta.io",
                "gmail.com",
                "foo.com"
              ],
              "status": "ok",
              "total": 1,
              "users": [
                {
                  "attributes": {},
                  "createTime": "2017-10-01T15:45:32.671Z",
                  "domain": "alerta.io",
                  "email": "admin@alerta.io",
                  "email_verified": false,
                  "href": "http://localhost:8080/user/107dcbe2-e5a9-4f6a-8c23-ce9379288bf5",
                  "id": "107dcbe2-e5a9-4f6a-8c23-ce9379288bf5",
                  "lastLogin": "2017-10-01T18:30:32.850Z",
                  "name": "Admin",
                  "provider": "basic",
                  "roles": [
                    "admin"
                  ],
                  "status": "active",
                  "text": "",
                  "updateTime": "2017-10-03T09:21:20.888Z"
                }
              ]
            }
        """

    @requests_mock.mock()
    def test_user(self, m):
        m.get('http://localhost:8080/users', text=self.user)
        users = self.client.get_users()
        self.assertEqual(users[0].name, 'Admin')
        self.assertEqual(sorted(users[0].roles), sorted(['admin']))
        self.assertEqual(users[0].status, 'active')
