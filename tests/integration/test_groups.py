import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_group(self):
        group = self.client.create_group(name='myGroup', text='test group')

        group_id = group.id

        self.assertEqual(group.name, 'myGroup')
        self.assertEqual(group.text, 'test group')

        group = self.client.update_group(group_id, name='newGroup', text='updated group text')
        self.assertEqual(group.name, 'newGroup')
        self.assertEqual(group.text, 'updated group text')

        group = self.client.create_group(name='myGroup2', text='test group2')

        groups = self.client.get_users_groups()
        self.assertEqual(len(groups), 2, groups)

        self.client.delete_group(group_id)

        groups = self.client.get_users_groups()
        self.assertEqual(len(groups), 1)
