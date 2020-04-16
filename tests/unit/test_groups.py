import unittest

import requests_mock

from alertaclient.api import Client


class GroupTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.key = """
            {
                "group": {
                    "count": 0,
                    "href": "http://localhost:8080/group/8ed5d256-4205-4dfc-b25d-185bd019cb21",
                    "id": "8ed5d256-4205-4dfc-b25d-185bd019cb21",
                    "name": "myGroup",
                    "text": "test group"
                },
                "id": "8ed5d256-4205-4dfc-b25d-185bd019cb21",
                "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_group(self, m):
        m.post('http://localhost:8080/group', text=self.key)
        group = self.client.create_group(name='myGroup', text='test group')
        self.assertEqual(group.name, 'myGroup')
        self.assertEqual(group.text, 'test group')
