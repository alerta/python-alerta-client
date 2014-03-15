
import unittest

from alerta import ApiClient, Alert


class TestAlert(unittest.TestCase):
    """
    Ensures Alert class is working as expected.
    """

    def setUp(self):
        """
        sets stuff up
        """
        self.environment = 'production'
        self.resource = 'router55'
        self.event = 'NODE:DOWN'
        self.text = 'foo is $f, bar was $B'
        self.tags = ['foo', 'bar', 'baz']

        self.client = ApiClient(host='localhost', port=9000)

    def test_send_alert(self):
        """
        Ensure a valid alert is created with some assigned values
        """
        alert = Alert(environment=self.environment, resource=self.resource, event=self.event)

        # self.assertEquals(alert.text, 'foo is foo, bar was baz')
        # self.assertEquals(alert.tags, {'Foo': '--foo--', 'Bar': 'bar'})

        response = self.client.send_alert(alert)
        id = response['receivedAlert']['_id']

        r = self.client.get_alerts(id=id)

if __name__ == '__main__':
    unittest.main()
