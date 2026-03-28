import json
import unittest

import requests_mock

from alertaclient.api import Client


class ClientAlertTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_get_alert(self, m):
        m.get('http://localhost:8080/alert/abc123', json={
            'alert': {
                'id': 'abc123',
                'resource': 'web01',
                'event': 'node_down',
                'environment': 'Production',
                'severity': 'critical',
                'status': 'open',
                'service': ['Web'],
                'tags': [],
                'correlate': [],
                'attributes': {},
                'createTime': '2020-01-01T00:00:00.000Z',
                'receiveTime': '2020-01-01T00:00:00.100Z',
                'lastReceiveTime': '2020-01-01T00:00:00.100Z',
            }
        })
        alert = self.client.get_alert('abc123')
        self.assertEqual(alert.id, 'abc123')
        self.assertEqual(alert.resource, 'web01')
        self.assertEqual(alert.severity, 'critical')

    @requests_mock.mock()
    def test_get_alerts(self, m):
        m.get('http://localhost:8080/alerts', json={
            'alerts': [
                {
                    'id': 'alert1',
                    'resource': 'web01',
                    'event': 'node_down',
                    'service': [],
                    'tags': [],
                    'correlate': [],
                    'attributes': {},
                    'createTime': '2020-01-01T00:00:00.000Z',
                    'receiveTime': '2020-01-01T00:00:00.000Z',
                    'lastReceiveTime': '2020-01-01T00:00:00.000Z',
                },
                {
                    'id': 'alert2',
                    'resource': 'web02',
                    'event': 'node_down',
                    'service': [],
                    'tags': [],
                    'correlate': [],
                    'attributes': {},
                    'createTime': '2020-01-01T00:00:00.000Z',
                    'receiveTime': '2020-01-01T00:00:00.000Z',
                    'lastReceiveTime': '2020-01-01T00:00:00.000Z',
                }
            ]
        })
        alerts = self.client.get_alerts()
        self.assertEqual(len(alerts), 2)
        self.assertEqual(alerts[0].resource, 'web01')
        self.assertEqual(alerts[1].resource, 'web02')

    @requests_mock.mock()
    def test_delete_alert(self, m):
        m.delete('http://localhost:8080/alert/abc123', json={})
        self.client.delete_alert('abc123')
        self.assertTrue(m.called)

    @requests_mock.mock()
    def test_set_status(self, m):
        m.put('http://localhost:8080/alert/abc123/status', json={'status': 'ok'})
        self.client.set_status('abc123', 'ack', text='acknowledged')
        data = m.request_history[0].json()
        self.assertEqual(data['status'], 'ack')
        self.assertEqual(data['text'], 'acknowledged')

    @requests_mock.mock()
    def test_action(self, m):
        m.put('http://localhost:8080/alert/abc123/action', json={'status': 'ok'})
        self.client.action('abc123', 'shelve', text='shelved for maintenance')
        data = m.request_history[0].json()
        self.assertEqual(data['action'], 'shelve')
        self.assertEqual(data['text'], 'shelved for maintenance')

    @requests_mock.mock()
    def test_tag_alert(self, m):
        m.put('http://localhost:8080/alert/abc123/tag', json={'status': 'ok'})
        self.client.tag_alert('abc123', ['linux', 'web'])
        data = m.request_history[0].json()
        self.assertEqual(data['tags'], ['linux', 'web'])

    @requests_mock.mock()
    def test_untag_alert(self, m):
        m.put('http://localhost:8080/alert/abc123/untag', json={'status': 'ok'})
        self.client.untag_alert('abc123', ['linux'])
        data = m.request_history[0].json()
        self.assertEqual(data['tags'], ['linux'])

    @requests_mock.mock()
    def test_update_attributes(self, m):
        m.put('http://localhost:8080/alert/abc123/attributes', json={'status': 'ok'})
        self.client.update_attributes('abc123', {'region': 'EU'})
        data = m.request_history[0].json()
        self.assertEqual(data['attributes'], {'region': 'EU'})

    @requests_mock.mock()
    def test_get_count(self, m):
        m.get('http://localhost:8080/alerts/count', json={
            'total': 42,
            'severityCounts': {'critical': 5, 'warning': 37},
            'statusCounts': {'open': 40, 'ack': 2}
        })
        total, severity_counts, status_counts = self.client.get_count()
        self.assertEqual(total, 42)
        self.assertEqual(severity_counts['critical'], 5)
        self.assertEqual(status_counts['open'], 40)

    @requests_mock.mock()
    def test_alert_note(self, m):
        m.put('http://localhost:8080/alert/abc123/note', json={
            'note': {
                'id': 'note1',
                'text': 'test note',
                'user': 'admin',
                'type': 'alert',
                'createTime': '2020-01-01T00:00:00.000Z',
                'updateTime': '2020-01-01T00:00:00.000Z',
            }
        })
        note = self.client.alert_note('abc123', 'test note')
        self.assertEqual(note.text, 'test note')
        self.assertEqual(note.user, 'admin')

    @requests_mock.mock()
    def test_get_alert_notes(self, m):
        m.get('http://localhost:8080/alert/abc123/notes', json={
            'notes': [
                {
                    'id': 'note1',
                    'text': 'first',
                    'user': 'admin',
                    'type': 'alert',
                    'createTime': '2020-01-01T00:00:00.000Z',
                    'updateTime': '2020-01-01T00:00:00.000Z',
                },
                {
                    'id': 'note2',
                    'text': 'second',
                    'user': 'admin',
                    'type': 'alert',
                    'createTime': '2020-01-01T00:00:01.000Z',
                    'updateTime': '2020-01-01T00:00:01.000Z',
                }
            ]
        })
        notes = self.client.get_alert_notes('abc123')
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].text, 'first')


class ClientBlackoutTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_create_blackout(self, m):
        m.post('http://localhost:8080/blackout', json={
            'blackout': {
                'id': 'b1',
                'environment': 'Production',
                'service': ['Web'],
                'tags': [],
                'startTime': '2020-01-01T00:00:00.000Z',
                'endTime': '2020-01-01T01:00:00.000Z',
                'duration': 3600,
            }
        })
        blackout = self.client.create_blackout('Production', service=['Web'], duration=3600)
        self.assertEqual(blackout.environment, 'Production')
        self.assertEqual(blackout.duration, 3600)
        data = m.request_history[0].json()
        self.assertEqual(data['environment'], 'Production')

    @requests_mock.mock()
    def test_get_blackouts(self, m):
        m.get('http://localhost:8080/blackouts', json={
            'blackouts': [
                {
                    'id': 'b1',
                    'environment': 'Production',
                    'service': [],
                    'tags': [],
                    'startTime': '2020-01-01T00:00:00.000Z',
                    'endTime': '2020-01-01T01:00:00.000Z',
                    'duration': 3600,
                }
            ]
        })
        blackouts = self.client.get_blackouts()
        self.assertEqual(len(blackouts), 1)
        self.assertEqual(blackouts[0].id, 'b1')

    @requests_mock.mock()
    def test_delete_blackout(self, m):
        m.delete('http://localhost:8080/blackout/b1', json={})
        self.client.delete_blackout('b1')
        self.assertTrue(m.called)


class ClientCustomerTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_create_customer(self, m):
        m.post('http://localhost:8080/customer', json={
            'customer': {'id': 'c1', 'match': 'example.com', 'customer': 'Example Corp'}
        })
        customer = self.client.create_customer('Example Corp', 'example.com')
        self.assertEqual(customer.customer, 'Example Corp')
        self.assertEqual(customer.match, 'example.com')

    @requests_mock.mock()
    def test_get_customers(self, m):
        m.get('http://localhost:8080/customers', json={
            'customers': [
                {'id': 'c1', 'match': 'example.com', 'customer': 'Example Corp'},
                {'id': 'c2', 'match': 'test.org', 'customer': 'Test Org'}
            ]
        })
        customers = self.client.get_customers()
        self.assertEqual(len(customers), 2)

    @requests_mock.mock()
    def test_delete_customer(self, m):
        m.delete('http://localhost:8080/customer/c1', json={})
        self.client.delete_customer('c1')
        self.assertTrue(m.called)


class ClientHeartbeatTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_get_heartbeats(self, m):
        m.get('http://localhost:8080/heartbeats', json={
            'heartbeats': [
                {
                    'id': 'hb1',
                    'origin': 'web01',
                    'tags': [],
                    'attributes': {},
                    'createTime': '2020-01-01T00:00:00.000Z',
                    'receiveTime': '2020-01-01T00:00:00.100Z',
                    'timeout': 300,
                    'status': 'ok',
                }
            ]
        })
        heartbeats = self.client.get_heartbeats()
        self.assertEqual(len(heartbeats), 1)
        self.assertEqual(heartbeats[0].origin, 'web01')

    @requests_mock.mock()
    def test_delete_heartbeat(self, m):
        m.delete('http://localhost:8080/heartbeat/hb1', json={})
        self.client.delete_heartbeat('hb1')
        self.assertTrue(m.called)


class ClientKeyTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_create_key(self, m):
        m.post('http://localhost:8080/key', json={
            'data': {
                'id': 'k1',
                'key': 'demo-key-12345',
                'user': 'admin@example.com',
                'scopes': ['read', 'write'],
                'text': 'test key',
                'expireTime': '2021-01-01T00:00:00.000Z',
            }
        })
        key = self.client.create_key('admin@example.com', scopes=['read', 'write'], text='test key')
        self.assertEqual(key.key, 'demo-key-12345')
        self.assertEqual(key.scopes, ['read', 'write'])

    @requests_mock.mock()
    def test_get_keys(self, m):
        m.get('http://localhost:8080/keys', json={
            'keys': [
                {
                    'id': 'k1',
                    'key': 'demo-key',
                    'user': 'admin',
                    'scopes': ['read'],
                    'text': '',
                }
            ]
        })
        keys = self.client.get_keys()
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0].type, 'read-only')

    @requests_mock.mock()
    def test_delete_key(self, m):
        m.delete('http://localhost:8080/key/k1', json={})
        self.client.delete_key('k1')
        self.assertTrue(m.called)


class ClientPermissionTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_create_perm(self, m):
        m.post('http://localhost:8080/perm', json={
            'permission': {'id': 'p1', 'match': 'admin', 'scopes': ['admin']}
        })
        perm = self.client.create_perm('admin', scopes=['admin'])
        self.assertEqual(perm.match, 'admin')
        self.assertEqual(perm.scopes, ['admin'])

    @requests_mock.mock()
    def test_get_perms(self, m):
        m.get('http://localhost:8080/perms', json={
            'permissions': [
                {'id': 'p1', 'match': 'admin', 'scopes': ['admin']},
                {'id': 'p2', 'match': 'user', 'scopes': ['read']}
            ]
        })
        perms = self.client.get_perms()
        self.assertEqual(len(perms), 2)


class ClientUserTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_create_user(self, m):
        m.post('http://localhost:8080/user', json={
            'user': {
                'id': 'u1',
                'name': 'Test User',
                'email': 'test@example.com',
                'status': 'active',
                'roles': ['user'],
                'text': '',
                'attributes': {},
                'createTime': '2020-01-01T00:00:00.000Z',
            }
        })
        user = self.client.create_user('Test User', 'test@example.com', 'secret', 'active', roles=['user'])
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.email, 'test@example.com')

    @requests_mock.mock()
    def test_get_users(self, m):
        m.get('http://localhost:8080/users', json={
            'users': [
                {
                    'id': 'u1',
                    'name': 'Admin',
                    'email': 'admin@example.com',
                    'status': 'active',
                    'roles': ['admin'],
                    'text': '',
                }
            ]
        })
        users = self.client.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].name, 'Admin')

    @requests_mock.mock()
    def test_delete_user(self, m):
        m.delete('http://localhost:8080/user/u1', json={})
        self.client.delete_user('u1')
        self.assertTrue(m.called)


class ClientGroupTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_create_group(self, m):
        m.post('http://localhost:8080/group', json={
            'group': {'id': 'g1', 'name': 'ops', 'text': 'Operations team', 'count': 0}
        })
        group = self.client.create_group('ops', 'Operations team')
        self.assertEqual(group.name, 'ops')
        self.assertEqual(group.text, 'Operations team')

    @requests_mock.mock()
    def test_get_users_groups(self, m):
        m.get('http://localhost:8080/groups', json={
            'groups': [
                {'id': 'g1', 'name': 'ops', 'text': 'Ops', 'count': 3},
                {'id': 'g2', 'name': 'dev', 'text': 'Dev', 'count': 5}
            ]
        })
        groups = self.client.get_users_groups()
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[1].count, 5)

    @requests_mock.mock()
    def test_delete_group(self, m):
        m.delete('http://localhost:8080/group/g1', json={})
        self.client.delete_group('g1')
        self.assertTrue(m.called)


class ClientAuthTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_login(self, m):
        m.post('http://localhost:8080/auth/login', json={'token': 'test-token'})
        result = self.client.login('admin', 'secret')
        self.assertEqual(result['token'], 'test-token')
        data = m.request_history[0].json()
        self.assertEqual(data['username'], 'admin')
        self.assertEqual(data['password'], 'secret')

    @requests_mock.mock()
    def test_config(self, m):
        m.get('http://localhost:8080/config', json={
            'auth_required': True,
            'provider': 'basic',
        })
        config = self.client.config()
        self.assertTrue(config['auth_required'])


class ClientErrorTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_send_alert_returns_message(self, m):
        m.post('http://localhost:8080/alert', json={
            'id': 'abc123',
            'message': 'alert received',
        })
        id, alert, message = self.client.send_alert(resource='web01', event='node_down')
        self.assertEqual(id, 'abc123')
        self.assertIsNone(alert)
        self.assertEqual(message, 'alert received')

    @requests_mock.mock()
    def test_get_alert_http_error(self, m):
        m.get('http://localhost:8080/alert/bad', status_code=404, json={
            'status': 'error',
            'message': 'not found',
        })
        with self.assertRaises(Exception):
            self.client.get_alert('bad')


class ClientSearchTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    @requests_mock.mock()
    def test_search_delegates_to_get_alerts(self, m):
        m.get('http://localhost:8080/alerts', json={'alerts': []})
        alerts = self.client.search()
        self.assertEqual(alerts, [])

    @requests_mock.mock()
    def test_get_alerts_with_query(self, m):
        m.get('http://localhost:8080/alerts', json={'alerts': []})
        self.client.get_alerts(query=[('severity', 'critical')])
        self.assertIn('severity=critical', m.request_history[0].url)

    @requests_mock.mock()
    def test_get_alerts_pagination(self, m):
        m.get('http://localhost:8080/alerts', json={'alerts': []})
        self.client.get_alerts(page=3, page_size=100)
        self.assertIn('page=3', m.request_history[0].url)
        self.assertIn('page-size=100', m.request_history[0].url)

    @requests_mock.mock()
    def test_get_history(self, m):
        m.get('http://localhost:8080/alerts/history', json={
            'history': [
                {
                    'id': 'h1',
                    'resource': 'web01',
                    'event': 'node_down',
                    'service': [],
                    'tags': [],
                    'attributes': {},
                    'updateTime': '2020-01-01T00:00:00.000Z',
                }
            ]
        })
        history = self.client.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].resource, 'web01')

    @requests_mock.mock()
    def test_get_environments(self, m):
        m.get('http://localhost:8080/environments', json={
            'environments': [{'environment': 'Production', 'count': 10}]
        })
        envs = self.client.get_environments()
        self.assertEqual(len(envs), 1)

    @requests_mock.mock()
    def test_get_services(self, m):
        m.get('http://localhost:8080/services', json={
            'services': [{'service': 'Web', 'count': 5}]
        })
        services = self.client.get_services()
        self.assertEqual(len(services), 1)

    @requests_mock.mock()
    def test_get_top10_count(self, m):
        m.get('http://localhost:8080/alerts/top10/count', json={'top10': []})
        result = self.client.get_top10_count()
        self.assertEqual(result, [])

    @requests_mock.mock()
    def test_get_top10_flapping(self, m):
        m.get('http://localhost:8080/alerts/top10/flapping', json={'top10': []})
        result = self.client.get_top10_flapping()
        self.assertEqual(result, [])

    @requests_mock.mock()
    def test_get_top10_standing(self, m):
        m.get('http://localhost:8080/alerts/top10/standing', json={'top10': []})
        result = self.client.get_top10_standing()
        self.assertEqual(result, [])
