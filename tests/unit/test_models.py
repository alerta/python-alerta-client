import unittest

from alertaclient.models.alert import Alert
from alertaclient.models.blackout import Blackout
from alertaclient.models.customer import Customer
from alertaclient.models.enums import ChangeType, NoteType, Scope
from alertaclient.models.group import Group
from alertaclient.models.heartbeat import Heartbeat
from alertaclient.models.key import ApiKey
from alertaclient.models.permission import Permission
from alertaclient.models.user import User


class AlertValidationTestCase(unittest.TestCase):

    def test_missing_resource_raises(self):
        with self.assertRaises(ValueError):
            Alert(resource='', event='node_down')

    def test_missing_event_raises(self):
        with self.assertRaises(ValueError):
            Alert(resource='web01', event='')

    def test_invalid_attribute_key_dot(self):
        with self.assertRaises(ValueError):
            Alert(resource='web01', event='node_down', attributes={'bad.key': 'value'})

    def test_invalid_attribute_key_dollar(self):
        with self.assertRaises(ValueError):
            Alert(resource='web01', event='node_down', attributes={'$bad': 'value'})

    def test_correlate_appends_event(self):
        alert = Alert(resource='web01', event='node_down', correlate=['node_up'])
        self.assertIn('node_down', alert.correlate)
        self.assertIn('node_up', alert.correlate)

    def test_correlate_no_duplicate(self):
        alert = Alert(resource='web01', event='node_down', correlate=['node_down', 'node_up'])
        self.assertEqual(alert.correlate.count('node_down'), 1)

    def test_defaults(self):
        alert = Alert(resource='web01', event='node_down')
        self.assertEqual(alert.status, 'unknown')
        self.assertEqual(alert.group, 'Misc')
        self.assertEqual(alert.event_type, 'exceptionAlert')
        self.assertEqual(alert.tags, [])
        self.assertEqual(alert.attributes, {})

    def test_get_id_short(self):
        alert = Alert(resource='web01', event='node_down', id='abcdef1234567890')
        self.assertEqual(alert.get_id(short=True), 'abcdef12')
        self.assertEqual(alert.get_id(short=False), 'abcdef1234567890')

    def test_repr(self):
        alert = Alert(resource='web01', event='node_down', id='test-id')
        r = repr(alert)
        self.assertIn('web01', r)
        self.assertIn('node_down', r)

    def test_parse_invalid_correlate_type(self):
        with self.assertRaises(ValueError):
            Alert.parse({'resource': 'web01', 'event': 'x', 'correlate': 'not-a-list'})

    def test_parse_invalid_service_type(self):
        with self.assertRaises(ValueError):
            Alert.parse({'resource': 'web01', 'event': 'x', 'service': 'not-a-list'})

    def test_parse_invalid_tags_type(self):
        with self.assertRaises(ValueError):
            Alert.parse({'resource': 'web01', 'event': 'x', 'tags': 'not-a-list'})

    def test_parse_invalid_attributes_type(self):
        with self.assertRaises(ValueError):
            Alert.parse({'resource': 'web01', 'event': 'x', 'attributes': 'not-a-dict'})

    def test_parse_invalid_timeout_type(self):
        with self.assertRaises(ValueError):
            Alert.parse({'resource': 'web01', 'event': 'x', 'timeout': 'not-an-int'})

    def test_tabular_joins_service(self):
        alert = Alert(resource='web01', event='node_down', id='abcdef1234567890', service=['Web', 'App'], tags=['a', 'b'])
        tab = alert.tabular(timezone='UTC')
        self.assertEqual(tab['service'], 'Web,App')
        self.assertEqual(tab['tags'], 'a,b')


class BlackoutValidationTestCase(unittest.TestCase):

    def test_missing_environment_raises(self):
        with self.assertRaises(ValueError):
            Blackout(environment='')

    def test_parse_invalid_service_type(self):
        with self.assertRaises(ValueError):
            Blackout.parse({
                'environment': 'Production',
                'service': 'not-a-list',
                'startTime': '2020-01-01T00:00:00.000Z',
                'endTime': '2020-01-01T01:00:00.000Z',
                'duration': 3600,
            })

    def test_repr(self):
        b = Blackout.parse({
            'id': 'b1',
            'environment': 'Production',
            'service': [],
            'tags': [],
            'startTime': '2020-01-01T00:00:00.000Z',
            'endTime': '2020-01-01T01:00:00.000Z',
            'duration': 3600,
        })
        self.assertIn('Production', repr(b))


class HeartbeatValidationTestCase(unittest.TestCase):

    def test_invalid_attribute_key(self):
        with self.assertRaises(ValueError):
            Heartbeat(origin='test', attributes={'bad.key': 'value'})

    def test_parse_invalid_tags_type(self):
        with self.assertRaises(ValueError):
            Heartbeat.parse({'tags': 'not-a-list'})

    def test_parse_invalid_attributes_type(self):
        with self.assertRaises(ValueError):
            Heartbeat.parse({'attributes': 'not-a-dict'})

    def test_parse_invalid_timeout_type(self):
        with self.assertRaises(ValueError):
            Heartbeat.parse({'timeout': 'not-an-int'})

    def test_latency(self):
        hb = Heartbeat.parse({
            'createTime': '2020-01-01T00:00:00.000Z',
            'receiveTime': '2020-01-01T00:00:00.500Z',
            'tags': [],
            'attributes': {},
            'timeout': 300,
        })
        self.assertEqual(hb.latency, 500)

    def test_defaults(self):
        hb = Heartbeat(origin='test')
        self.assertEqual(hb.status, 'unknown')
        self.assertEqual(hb.event_type, 'Heartbeat')
        self.assertEqual(hb.tags, [])


class GroupValidationTestCase(unittest.TestCase):

    def test_missing_name_raises(self):
        with self.assertRaises(ValueError):
            Group(name='', text='test')

    def test_repr(self):
        g = Group(name='ops', text='Operations')
        self.assertIn('ops', repr(g))


class ApiKeyTestCase(unittest.TestCase):

    def test_type_readonly(self):
        key = ApiKey(user='admin', scopes=['read'])
        self.assertEqual(key.type, 'read-only')

    def test_type_readwrite(self):
        key = ApiKey(user='admin', scopes=['read', 'write:alerts'])
        self.assertEqual(key.type, 'read-write')

    def test_type_admin(self):
        key = ApiKey(user='admin', scopes=['admin'])
        self.assertEqual(key.type, 'read-write')

    def test_parse_invalid_scopes_type(self):
        with self.assertRaises(ValueError):
            ApiKey.parse({'scopes': 'not-a-list'})


class PermissionValidationTestCase(unittest.TestCase):

    def test_parse_invalid_scopes_type(self):
        with self.assertRaises(ValueError):
            Permission.parse({'scopes': 'not-a-list'})

    def test_tabular(self):
        perm = Permission(match='admin', scopes=['read', 'write'])
        tab = perm.tabular()
        self.assertEqual(tab['scopes'], 'read,write')


class UserTestCase(unittest.TestCase):

    def test_domain(self):
        user = User(name='Test', email='test@example.com', roles=['user'], text='')
        self.assertEqual(user.domain, 'example.com')

    def test_domain_no_at(self):
        user = User(name='Test', email='admin', roles=['user'], text='')
        self.assertIsNone(user.domain)

    def test_defaults(self):
        user = User(name='Test', email='test@example.com', roles=[], text='')
        self.assertEqual(user.status, 'active')

    def test_email_verified_tabular(self):
        user = User(name='Test', email='t@t.com', roles=[], text='', email_verified=True)
        self.assertEqual(user.tabular(timezone='UTC')['email_verified'], 'yes')

        user2 = User(name='Test', email='t@t.com', roles=[], text='', email_verified=False)
        self.assertEqual(user2.tabular(timezone='UTC')['email_verified'], 'no')


class CustomerTestCase(unittest.TestCase):

    def test_repr(self):
        c = Customer(match='example.com', customer='Example')
        self.assertIn('example.com', repr(c))


class ScopeTestCase(unittest.TestCase):

    def test_action(self):
        s = Scope('read:alerts')
        self.assertEqual(s.action, 'read')

    def test_resource(self):
        s = Scope('write:heartbeats')
        self.assertEqual(s.resource, 'heartbeats')

    def test_resource_none(self):
        s = Scope('admin')
        self.assertIsNone(s.resource)

    def test_from_str(self):
        s = Scope.from_str('read', 'alerts')
        self.assertEqual(s, 'read:alerts')

    def test_from_str_no_resource(self):
        s = Scope.from_str('admin')
        self.assertEqual(s, 'admin')


class EnumTestCase(unittest.TestCase):

    def test_change_type_values(self):
        self.assertEqual(ChangeType.open.value, 'open')
        self.assertEqual(ChangeType.severity.value, 'severity')

    def test_note_type_values(self):
        self.assertEqual(NoteType.alert.value, 'alert')
        self.assertEqual(NoteType.key.value, 'api-key')
