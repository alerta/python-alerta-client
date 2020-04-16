import unittest

import requests_mock

from alertaclient.api import Client


class CustomerTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

        self.customer = """
            {
              "customer": {
                "customer": "ACME Corp.",
                "href": "http://localhost:8080/customer/9bb97023-186e-4744-a59d-d18f641eee52",
                "id": "9bb97023-186e-4744-a59d-d18f641eee52",
                "match": "example.com"
              },
              "id": "9bb97023-186e-4744-a59d-d18f641eee52",
              "status": "ok"
            }
        """

    @requests_mock.mock()
    def test_customer(self, m):
        m.post('http://localhost:8080/customer', text=self.customer)
        customer = self.client.create_customer(customer='ACME Corp.', match='example.com')
        self.assertEqual(customer.customer, 'ACME Corp.')
        self.assertEqual(customer.match, 'example.com')
