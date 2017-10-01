
import json
import logging
import os

import requests
from requests.auth import AuthBase

from alertaclient.exceptions import AuthError, UnknownError
from alertaclient.models.alert import Alert
from alertaclient.models.blackout import Blackout
from alertaclient.models.customer import Customer
from alertaclient.models.heartbeat import Heartbeat
from alertaclient.models.history import RichHistory
from alertaclient.models.key import ApiKey
from alertaclient.models.permission import Permission
from alertaclient.models.user import User
from alertaclient.utils import DateTime

try:
    from urllib.parse import urlparse, urlencode
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode

logger = logging.getLogger('alerta.client')


class Client(object):

    DEFAULT_ENDPOINT = 'http://localhost:8080'

    def __init__(self, endpoint=None, key=None, token=None, timeout=5.0, ssl_verify=True, debug=False):
        self.endpoint = endpoint or os.environ.get('ALERTA_ENDPOINT', self.DEFAULT_ENDPOINT)

        if debug:
            try:  # for Python 3
                from http.client import HTTPConnection
            except ImportError:
                from httplib import HTTPConnection
            HTTPConnection.debuglevel = 1

        key = key or os.environ.get('ALERTA_API_KEY', '')
        self.client = HTTPClient(self.endpoint, key, token, timeout, ssl_verify, debug)

    # Alerts
    def send_alert(self, **kwargs):
        r = self.client.post('/alert', kwargs)
        return Alert.parse(r['alert'])

    def get_alert(self, id):
        return Alert.parse(self.client.get('/alert/%s' % id)['alert'])

    def set_status(self, id, status, text):
        data = {
            'status': status,
            'text': text
        }
        return self.client.put('/alert/%s/status' % id, data)

    def tag_alert(self, id, tags):
        return self.client.put('/alert/%s/tag' % id, {"tags": tags})

    def untag_alert(self, id, tags):
        return self.client.put('/alert/%s/untag' % id, {"tags": tags})

    def update_attributes(self, id, attributes):
        data = {
            'attributes': attributes
        }
        return self.client.put('/alert/%s/attributes' % id, data)

    def delete_alert(self, id):
        return self.client.delete('/alert/%s' % id)

    def search(self, query=None):
        return self.get_alerts(query)

    def get_alerts(self, query=None):
        r = self.client.get('/alerts', query)
        return [Alert.parse(a) for a in r['alerts']]

    def get_history(self, query=None):
        r = self.client.get('/alerts/history', query)
        return [RichHistory.parse(a) for a in r['history']]

    def get_count(self, query=None):
        counts = self.client.get('/alerts/count', query)
        return counts['total'], counts['severityCounts'], counts['statusCounts']

    def get_top10_count(self, query=None):
        counts = self.client.get('/alerts/top10/count', query)
        return counts['top10']

    def get_top10_flapping(self, query=None):
        counts = self.client.get('/alerts/top10/flapping', query)
        return counts['top10']

    def get_environments(self, query=None):
        counts = self.client.get('/environments', query)
        return counts['environments']

    def get_services(self, query=None):
        counts = self.client.get('/services', query)
        return counts['services']

    # Blackouts
    def create_blackout(self, environment, service, resource, event, group, tag, start, duration):
        data = {
            'environment': environment,
            'service': service,
            'resource': resource,
            'event': event,
            'group': group,
            'tags': tag,
            'startTime': start,
            'duration': duration
        }
        r = self.client.post('/blackout', data)
        return Blackout.parse(r['blackout'])

    def get_blackouts(self, query=None):
        r = self.client.get('/blackouts', query)
        return [Blackout.parse(b) for b in r['blackouts']]

    def delete_blackout(self, id):
        return self.client.delete('/blackout/%s' % id)

    # Customers
    def create_customer(self, customer, match):
        data = {
            'customer': customer,
            'match': match
        }
        r = self.client.post('/customer', data)
        return Customer.parse(r['customer'])

    def get_customers(self, query=None):
        r = self.client.get('/customers', query)
        return [Customer.parse(c) for c in r['customers']]

    def delete_customer(self, id):
        return self.client.delete('/customer/%s' % id)

    # Heartbeats
    def heartbeat(self, **kwargs):
        r = self.client.post('/heartbeat', kwargs)
        return Heartbeat.parse(r['heartbeat'])

    def get_heartbeat(self, id):
        return Heartbeat.parse(self.client.get('/heartbeat/%s' % id)['heartbeat'])

    def get_heartbeats(self, query=None):
        r = self.client.get('/heartbeats', query)
        return [Heartbeat.parse(hb) for hb in r['heartbeats']]

    def delete_heartbeat(self, id):
        return self.client.delete('/heartbeat/%s' % id)

    # API Keys
    def create_key(self, username, scopes=None, expires=None, text=''):
        data = {
            'user': username,
            'scopes': scopes or list(),
            'text': text
        }
        if expires:
            data['expireTime'] = DateTime.iso8601(expires)
        r = self.client.post('/key', data)
        return ApiKey.parse(r['data'])

    def get_keys(self, query=None):
        r = self.client.get('/keys', query)
        return [ApiKey.parse(k) for k in r['keys']]

    def delete_key(self, id):
        return self.client.delete('/key/%s' % id)

    # Permissions
    def create_perm(self, role, scopes):
        data = {
            'match': role,
            'scopes': scopes
        }
        r = self.client.post('/perm', data)
        return Permission.parse(r['permission'])

    def get_perms(self, query=None):
        r = self.client.get('/perms', query)
        return [Permission.parse(p) for p in r['permissions']]

    def delete_perm(self, id):
        return self.client.delete('/perm/%s' % id)

    # Users
    def login(self, username, password):
        data = {
            'username': username,
            'password': password
        }
        r = self.client.post('/auth/login', data)
        if 'token' in r:
            return r['token']
        else:
            raise AuthError

    def get_users(self, query=None):
        r = self.client.get('/users', query)
        return [User.parse(u) for u in r['users']]

    def update_user(self, id, **kwargs):
        data = {
            'name': kwargs.get('name'),
            'email': kwargs.get('email'),
            'password': kwargs.get('password'),
            'status': kwargs.get('status'),
            'roles': kwargs.get('roles'),
            'text': kwargs.get('text'),
            'email_verified': kwargs.get('email_verified')
        }
        return self.client.put('/user/{}'.format(id), data)

    def update_user_attributes(self, id, attributes):
        pass

    def delete_user(self, id):
        return self.client.delete('/user/%s' % id)

    def userinfo(self):
        return self.client.get('/userinfo')

    # Management
    def mgmt_status(self):
        return self.client.get('/management/status')


class ApiAuth(AuthBase):

    def __init__(self, api_key=None, auth_token=None):
        self.api_key = api_key
        self.auth_token = auth_token

    def __call__(self, r):
        if self.auth_token:
            r.headers['Authorization'] = 'Bearer {}'.format(self.auth_token)
        else:
            r.headers['Authorization'] = 'Key {}'.format(self.api_key)
        return r


class HTTPClient(object):

    def __init__(self, endpoint, key=None, token=None, timeout=30.0, ssl_verify=True, debug=False):
        self.endpoint = endpoint
        self.auth = ApiAuth(api_key=key, auth_token=token)

        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = ssl_verify  # or use REQUESTS_CA_BUNDLE env var

        self.debug = debug

    def get(self, path, query=None):
        query = query or tuple()
        url = self.endpoint + path + '?' + urlencode(query, doseq=True)
        try:
            response = self.session.get(url, auth=self.auth, timeout=self.timeout)
        except requests.exceptions.RequestException:
            raise
        return self._handle_error(response)

    def post(self, path, data=None):
        url = self.endpoint + path
        headers = {'Content-Type': 'application/json'}
        try:
            response = self.session.post(url, data=json.dumps(data), headers=headers, auth=self.auth, timeout=self.timeout)
        except requests.exceptions.RequestException:
            raise
        return self._handle_error(response)

    def put(self, path, data=None):
        url = self.endpoint + path
        headers = {'Content-Type': 'application/json'}
        try:
            response = self.session.put(url, data=json.dumps(data), headers=headers, auth=self.auth, timeout=self.timeout)
        except requests.exceptions.RequestException:
            raise
        return self._handle_error(response)

    def delete(self, path):
        url = self.endpoint + path

        try:
            response = self.session.delete(url, auth=self.auth, timeout=self.timeout)
        except requests.exceptions.RequestException:
            raise
        return self._handle_error(response)

    def _handle_error(self, response):
        if self.debug:
            print('\nbody: {}'.format(response.text))
        resp = response.json()
        status = resp.get('status', None)
        if status == 'ok':
            return resp
        if status == 'error':
            raise UnknownError(resp['message'])
        return resp
