import unittest

from alertaclient.api import Client


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(endpoint='http://alerta:8080/api', key='demo-key')

    def test_notes(self):
        # add tests here when /notes endpoints are created
        pass
