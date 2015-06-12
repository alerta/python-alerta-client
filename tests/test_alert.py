
import unittest
import datetime

from alerta.alert import Alert


class TestAlert(unittest.TestCase):

    def setUp(self):

        self.RESOURCE = 'router55'
        self.EVENT = 'Node_Down'
        self.ENVIRONMENT = 'Production'
        self.SEVERITY = 'major'
        self.CORRELATE = ['Node_Down', 'Node_Up']
        self.STATUS = 'open'
        self.SERVICE = ['Common']
        self.GROUP = 'Network'
        self.VALUE = 'ping failed'
        self.TEXT = 'Node is not responding to ping'
        self.TAGS = ['location:london', 'vendor:cisco']
        self.ATTRIBUTES = {'thresholdInfo': 'n/a'}
        self.ORIGIN = 'test_alert'
        self.EVENT_TYPE = 'exceptionAlert'
        self.CREATE_TIME = datetime.datetime.utcnow()
        self.TIMEOUT = 86400
        self.RAW_DATA = 'lots of raw text'

        self.DUPLICATE_COUNT = 0
        self.REPEAT = False
        self.PREVIOUS_SEVERITY = 'unknown'
        self.TREND_INDICATION = 'moreSevere'
        self.RECEIVE_TIME = datetime.datetime.utcnow()

    def test_alert_defaults(self):
        """
        Ensures a valid alert is created with default values
        """
        alert = Alert(self.RESOURCE, self.EVENT)

        self.assertEquals(alert.resource, self.RESOURCE)
        self.assertEquals(alert.event, self.EVENT)
        self.assertEquals(alert.severity, 'normal')
        self.assertEquals(alert.group, 'Misc')
        self.assertEquals(alert.timeout, self.TIMEOUT)

    def test_alert_with_some_values(self):
        """
        Ensure a valid alert is created with some assigned values
        """
        alert = Alert(
            self.RESOURCE,
            self.EVENT,
            environment=self.ENVIRONMENT,
            severity=self.SEVERITY,
            correlate=self.CORRELATE,
            status=self.STATUS,
            service=self.SERVICE,
            group=self.GROUP,
            value=self.VALUE,
            text=self.TEXT,
            tags=self.TAGS,
            attributes=self.ATTRIBUTES,
            origin=self.ORIGIN,
            event_type=self.EVENT_TYPE,
            create_time=self.CREATE_TIME,
            timeout=self.TIMEOUT,
            raw_data=self.RAW_DATA
        )

        self.assertEquals(alert.resource, self.RESOURCE)
        self.assertEquals(alert.event, self.EVENT)
        self.assertEquals(alert.environment, self.ENVIRONMENT)
        self.assertEquals(alert.severity, self.SEVERITY)
        self.assertEquals(alert.correlate, self.CORRELATE)
        self.assertEquals(alert.service, self.SERVICE)
        self.assertEquals(alert.tags, self.TAGS)
        self.assertEquals(alert.attributes, self.ATTRIBUTES)

    def test_alert_receive_now(self):
        """
        Ensure receive time is stamped.
        """
        alert = Alert(
            self.RESOURCE,
            self.EVENT,
            environment=self.ENVIRONMENT,
            severity=self.SEVERITY
        )

        alert.receive_now()
        self.assertIsInstance(alert.receive_time, datetime.datetime)
