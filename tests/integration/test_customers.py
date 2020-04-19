import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://api:8080', key='demo-key')

    def test_customer(self):
        customer = self.client.create_customer(customer='ACME Corp.', match='example.com')

        customer_id = customer.id

        self.assertEqual(customer.customer, 'ACME Corp.')
        self.assertEqual(customer.match, 'example.com')

        customer = self.client.update_customer(customer_id, customer='Foo Corp.', match='foo.com')

        self.assertEqual(customer.customer, 'Foo Corp.')
        self.assertEqual(customer.match, 'foo.com')

        customer = self.client.create_customer(customer='Quetzal Inc.', match='quetzal.io')

        customers = self.client.get_customers()
        self.assertEqual(len(customers), 2)

        self.client.delete_customer(customer_id)

        customers = self.client.get_customers()
        self.assertEqual(len(customers), 1)
