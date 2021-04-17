import json
import logging
import os
import uuid
from datetime import datetime
from http.client import HTTPConnection
from urllib.parse import urlencode

import requests
from requests.auth import AuthBase, HTTPBasicAuth
from requests_hawk import HawkAuth

from alertaclient.auth.utils import merge
from alertaclient.exceptions import UnknownError
from alertaclient.models.alert import Alert
from alertaclient.models.blackout import Blackout
from alertaclient.models.customer import Customer
from alertaclient.models.enums import Scope
from alertaclient.models.group import Group
from alertaclient.models.heartbeat import Heartbeat
from alertaclient.models.history import RichHistory
from alertaclient.models.key import ApiKey
from alertaclient.models.note import Note
from alertaclient.models.permission import Permission
from alertaclient.models.user import User
from alertaclient.utils import CustomJsonEncoder, DateTime

logger = logging.getLogger('alerta.client')


class Client:

    DEFAULT_ENDPOINT = 'http://localhost:8080'

    def __init__(self, endpoint=None, key=None, secret=None, token=None, username=None, password=None, timeout=5.0,
                 ssl_verify=True, ssl_cert=None, ssl_key=None, headers=None, debug=False):
        self.endpoint = endpoint or os.environ.get('ALERTA_ENDPOINT', self.DEFAULT_ENDPOINT)

        if debug:
            HTTPConnection.debuglevel = 1

        key = key or os.environ.get('ALERTA_API_KEY', '')
        self.http = HTTPClient(self.endpoint, key, secret, token, username, password,
                               timeout, ssl_verify, ssl_cert, ssl_key, headers, debug)

    # Alerts
    def send_alert(self, resource, event, **kwargs):
        data = {
            'id': kwargs.get('id'),
            'resource': resource,
            'event': event,
            'environment': kwargs.get('environment'),
            'severity': kwargs.get('severity'),
            'correlate': kwargs.get('correlate', None) or list(),
            'service': kwargs.get('service', None) or list(),
            'group': kwargs.get('group'),
            'value': kwargs.get('value'),
            'text': kwargs.get('text'),
            'tags': kwargs.get('tags', None) or list(),
            'attributes': kwargs.get('attributes', None) or dict(),
            'origin': kwargs.get('origin'),
            'type': kwargs.get('type'),
            'createTime': datetime.utcnow(),
            'timeout': kwargs.get('timeout'),
            'rawData': kwargs.get('raw_data'),
            'customer': kwargs.get('customer')
        }
        r = self.http.post('/alert', data)
        alert = Alert.parse(r['alert']) if 'alert' in r else None
        return r.get('id', '-'), alert, r.get('message', None)

    def get_alert(self, id):
        return Alert.parse(self.http.get('/alert/%s' % id)['alert'])

    def set_status(self, id, status, text='', timeout=None):
        data = {
            'status': status,
            'text': text,
            'timeout': timeout
        }
        return self.http.put('/alert/%s/status' % id, data)

    def action(self, id, action, text='', timeout=None):
        data = {
            'action': action,
            'text': text,
            'timeout': timeout
        }
        return self.http.put('/alert/%s/action' % id, data)

    def tag_alert(self, id, tags):
        return self.http.put('/alert/%s/tag' % id, {'tags': tags})

    def untag_alert(self, id, tags):
        return self.http.put('/alert/%s/untag' % id, {'tags': tags})

    def update_attributes(self, id, attributes):
        data = {
            'attributes': attributes
        }
        return self.http.put('/alert/%s/attributes' % id, data)

    def delete_alert(self, id):
        return self.http.delete('/alert/%s' % id)

    def search(self, query=None, page=1, page_size=None):
        return self.get_alerts(query, page, page_size)

    def get_alerts(self, query=None, page=1, page_size=None):
        r = self.http.get('/alerts', query, page=page, page_size=page_size)
        return [Alert.parse(a) for a in r['alerts']]

    def get_history(self, query=None, page=1, page_size=None):
        r = self.http.get('/alerts/history', query, page=page, page_size=page_size)
        return [RichHistory.parse(a) for a in r['history']]

    def get_count(self, query=None):
        counts = self.http.get('/alerts/count', query)
        return counts['total'], counts['severityCounts'], counts['statusCounts']

    def get_top10_count(self, query=None):
        counts = self.http.get('/alerts/top10/count', query)
        return counts['top10']

    def get_top10_flapping(self, query=None):
        counts = self.http.get('/alerts/top10/flapping', query)
        return counts['top10']

    def get_top10_standing(self, query=None):
        counts = self.http.get('/alerts/top10/standing', query)
        return counts['top10']

    def get_environments(self, query=None):
        r = self.http.get('/environments', query)
        return r['environments']

    def get_services(self, query=None):
        r = self.http.get('/services', query)
        return r['services']

    def get_groups(self, query=None):
        r = self.http.get('/alerts/groups', query)
        return r['groups']

    def get_tags(self, query=None):
        r = self.http.get('/alerts/tags', query)
        return r['tags']

    def alert_note(self, id, text):
        data = {
            'text': text
        }
        r = self.http.put('/alert/{}/note'.format(id), data)
        return Note.parse(r['note'])

    def get_alert_notes(self, id, page=1, page_size=None):
        r = self.http.get('/alert/{}/notes'.format(id), page=page, page_size=page_size)
        return [Note.parse(n) for n in r['notes']]

    def update_alert_note(self, id, note_id, text):
        data = {
            'text': text,
        }
        r = self.http.put('/alert/{}/note/{}'.format(id, note_id), data)
        return Note.parse(r['note'])

    def delete_alert_note(self, id, note_id):
        return self.http.delete('/alert/{}/note/{}'.format(id, note_id))

    # Blackouts
    def create_blackout(self, environment, service=None, resource=None, event=None, group=None, tags=None,
                        origin=None, customer=None, start=None, duration=None, text=None):
        data = {
            'environment': environment,
            'service': service or list(),
            'resource': resource,
            'event': event,
            'group': group,
            'tags': tags or list(),
            'origin': origin,
            'customer': customer,
            'startTime': start,
            'duration': duration,
            'text': text
        }
        r = self.http.post('/blackout', data)
        return Blackout.parse(r['blackout'])

    def get_blackout(self, id):
        return Blackout.parse(self.http.get('/blackout/%s' % id)['blackout'])

    def get_blackouts(self, query=None):
        r = self.http.get('/blackouts', query)
        return [Blackout.parse(b) for b in r['blackouts']]

    def update_blackout(self, id, **kwargs):
        data = {
            'customer': kwargs.get('customer'),
            'environment': kwargs.get('environment'),
            'service': kwargs.get('service'),
            'resource': kwargs.get('resource'),
            'event': kwargs.get('event'),
            'group': kwargs.get('group'),
            'tags': kwargs.get('tags'),
            'origin': kwargs.get('origin'),
            'startTime': kwargs.get('startTime'),
            'endTime': kwargs.get('endTime'),
            'text': kwargs.get('text'),
        }

        r = self.http.put('/blackout/{}'.format(id), data)
        return Blackout.parse(r['blackout'])

    def delete_blackout(self, id):
        return self.http.delete('/blackout/%s' % id)

    # Customers
    def create_customer(self, customer, match):
        data = {
            'customer': customer,
            'match': match
        }
        r = self.http.post('/customer', data)
        return Customer.parse(r['customer'])

    def get_customer(self):
        return Customer.parse(self.http.get('/customer/%s' % id)['customer'])

    def get_customers(self, query=None):
        r = self.http.get('/customers', query)
        return [Customer.parse(c) for c in r['customers']]

    def update_customer(self, id, **kwargs):
        data = {
            'match': kwargs.get('match'),
            'customer': kwargs.get('customer')
        }
        r = self.http.put('/customer/{}'.format(id), data)
        return Customer.parse(r['customer'])

    def delete_customer(self, id):
        return self.http.delete('/customer/%s' % id)

    # Heartbeats
    def heartbeat(self, origin, tags=None, attributes=None, timeout=None, customer=None):
        data = {
            'origin': origin,
            'tags': tags or list(),
            'attributes': attributes or dict(),
            'timeout': timeout,
            'createTime': datetime.utcnow(),
            'customer': customer
        }
        r = self.http.post('/heartbeat', data)
        return Heartbeat.parse(r['heartbeat'])

    def get_heartbeat(self, id):
        return Heartbeat.parse(self.http.get('/heartbeat/%s' % id)['heartbeat'])

    def get_heartbeats(self, query=None):
        r = self.http.get('/heartbeats', query)
        return [Heartbeat.parse(hb) for hb in r['heartbeats']]

    def delete_heartbeat(self, id):
        return self.http.delete('/heartbeat/%s' % id)

    # API Keys
    def create_key(self, username, scopes=None, expires=None, text='', customer=None):
        data = {
            'user': username,
            'scopes': scopes or list(),
            'text': text,
            'customer': customer
        }
        if expires:
            data['expireTime'] = DateTime.iso8601(expires)
        r = self.http.post('/key', data)
        return ApiKey.parse(r['data'])

    def get_key(self):
        return ApiKey.parse(self.http.get('/key/%s' % id)['key'])

    def get_keys(self, query=None):
        r = self.http.get('/keys', query)
        return [ApiKey.parse(k) for k in r['keys']]

    def update_key(self, id, **kwargs):
        data = {
            'scopes': kwargs.get('scopes'),
            'text': kwargs.get('text'),
            'expireTime': kwargs.get('expireTime'),
            'customer': kwargs.get('customer')
        }
        r = self.http.put('/key/{}'.format(id), data)
        return ApiKey.parse(r['key'])

    def delete_key(self, id):
        return self.http.delete('/key/%s' % id)

    # Permissions
    def create_perm(self, role, scopes=None):
        data = {
            'match': role,
            'scopes': scopes or list()
        }
        r = self.http.post('/perm', data)
        return Permission.parse(r['permission'])

    def get_perm(self):
        return Permission.parse(self.http.get('/perm/%s' % id)['perm'])

    def get_perms(self, query=None):
        r = self.http.get('/perms', query)
        return [Permission.parse(p) for p in r['permissions']]

    def update_perm(self, id, **kwargs):
        data = {
            'match': kwargs.get('match'),  # role
            'scopes': kwargs.get('scopes')
        }
        r = self.http.put('/perm/{}'.format(id), data)
        return Permission.parse(r['permission'])

    def delete_perm(self, id):
        return self.http.delete('/perm/%s' % id)

    def get_scopes(self):
        r = self.http.get('/scopes')
        return [Scope(s) for s in r['scopes']]

    # Users
    def signup(self, name, email, password, status, attributes=None, text=''):
        data = {
            'name': name,
            'email': email,
            'password': password,
            'status': status,
            'attributes': attributes or dict(),
            'text': text
        }
        return self.http.post('/auth/signup', data)

    def create_user(self, name, email, password, status, roles=None, attributes=None, text='', email_verified=False):
        data = {
            'name': name,
            'email': email,
            'password': password,
            'status': status,
            'roles': roles or list(),
            'attributes': attributes or dict(),
            'text': text,
            'email_verified': email_verified
        }
        r = self.http.post('/user', data)
        return User.parse(r['user'])

    def get_user(self, id):
        return User.parse(self.http.get('/user/%s' % id)['user'])

    def get_user_groups(self, id):
        r = self.http.get('/user/{}/groups'.format(id))
        return [Group.parse(g) for g in r['groups']]

    def get_me(self):
        return User.parse(self.http.get('/user/me')['user'])

    def get_me_attributes(self):
        return self.http.get('/user/me/attributes')['attributes']

    def get_users(self, query=None):
        r = self.http.get('/users', query)
        return [User.parse(u) for u in r['users']]

    def update_user(self, id, **kwargs):
        data = {
            'name': kwargs.get('name'),
            'email': kwargs.get('email'),
            'password': kwargs.get('password'),
            'status': kwargs.get('status'),
            'roles': kwargs.get('roles', None) or list(),
            'attributes': kwargs.get('attributes', None) or dict(),
            'text': kwargs.get('text'),
            'email_verified': kwargs.get('email_verified')
        }
        r = self.http.put('/user/{}'.format(id), data)
        return User.parse(r['user'])

    def update_me(self, **kwargs):
        data = {
            'name': kwargs.get('name'),
            'email': kwargs.get('email'),
            'password': kwargs.get('password'),
            'status': kwargs.get('status'),
            'attributes': kwargs.get('attributes', None) or dict(),
            'text': kwargs.get('text')
        }
        r = self.http.put('/user/me', data)
        return User.parse(r['user'])

    def update_user_attributes(self, id, attributes):
        data = {
            'attributes': attributes
        }
        return self.http.put('/user/%s/attributes' % id, data)

    def update_me_attributes(self, attributes):
        data = {
            'attributes': attributes
        }
        return self.http.put('/user/me/attributes' % data)

    def delete_user(self, id):
        return self.http.delete('/user/%s' % id)

    # Auth
    def login(self, username, password):
        data = {
            'username': username,
            'password': password
        }
        return self.http.post('/auth/login', data)

    def token(self, provider, data):
        if provider == 'azure':
            return self.http.post('/auth/azure', data)
        if provider == 'github':
            return self.http.post('/auth/github', data)
        if provider == 'gitlab':
            return self.http.post('/auth/gitlab', data)
        if provider == 'google':
            return self.http.post('/auth/google', data)
        if provider == 'openid':
            return self.http.post('/auth/openid', data)

    def userinfo(self):
        return self.http.get('/userinfo')

    def config(self):
        return self.http.get('/config')

    # Groups
    def create_group(self, name, text):
        data = {
            'name': name,
            'text': text
        }
        r = self.http.post('/group', data)
        return Group.parse(r['group'])

    def get_group(self):
        return Group.parse(self.http.get('/group/%s' % id)['group'])

    def get_group_users(self, id):
        r = self.http.get('/group/{}/users'.format(id))
        return [User.parse(u) for u in r['users']]

    def get_users_groups(self, query=None):
        r = self.http.get('/groups', query)
        return [Group.parse(g) for g in r['groups']]

    def update_group(self, id, **kwargs):
        data = {
            'name': kwargs.get('name'),
            'text': kwargs.get('text')
        }
        r = self.http.put('/group/{}'.format(id), data)
        return Group.parse(r['group'])

    def add_user_to_group(self, group_id, user_id):
        return self.http.put('/group/{}/user/{}'.format(group_id, user_id))

    def remove_user_from_group(self, group_id, user_id):
        return self.http.delete('/group/{}/user/{}'.format(group_id, user_id))

    def delete_group(self, id):
        return self.http.delete('/group/%s' % id)

    # Management
    def mgmt_status(self):
        return self.http.get('/management/status')

    def housekeeping(self, expired_delete_hours=None, info_delete_hours=None):
        # This endpoint isn't currently JSON-encoded.
        url = self.http.endpoint + '/management/housekeeping'
        params = dict()
        if expired_delete_hours is not None:
            params['expired'] = expired_delete_hours
        if info_delete_hours is not None:
            params['info'] = info_delete_hours
        response = self.http.session.get(url, auth=self.http.auth, timeout=self.http.timeout, params=params)
        if response.status_code != 200:
            raise UnknownError(response.text)


class ApiKeyAuth(AuthBase):

    def __init__(self, api_key=None, auth_token=None):
        self.api_key = api_key
        self.auth_token = auth_token

    def __call__(self, r):
        r.headers['Authorization'] = 'Key {}'.format(self.api_key)
        return r


class TokenAuth(AuthBase):

    def __init__(self, auth_token=None):
        self.auth_token = auth_token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer {}'.format(self.auth_token)
        return r


class HTTPClient:

    DEFAULT_PAGE_NUMBER = 1
    DEFAULT_PAGE_SIZE = 50

    def __init__(
        self,
        endpoint,
        key=None,
        secret=None,
        token=None,
        username=None,
        password=None,
        timeout=30.0,
        ssl_verify=True,
        ssl_cert=None,
        ssl_key=None,
        headers=None,
        debug=False,
    ):
        self.endpoint = endpoint
        self.auth = None

        if username:
            self.auth = HTTPBasicAuth(username, password)
        elif secret:
            self.auth = HawkAuth(id=key, key=secret)  # HMAC
        elif key:
            self.auth = ApiKeyAuth(api_key=key)
        elif token:
            self.auth = TokenAuth(token)

        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = ssl_verify  # or use REQUESTS_CA_BUNDLE env var

        if ssl_cert:
            self.session.cert = (ssl_cert, ssl_key)

        self.headers = headers or dict()
        merge(self.headers, self.default_headers())

        self.debug = debug

    @staticmethod
    def default_headers():
        return {
            'X-Request-ID': str(uuid.uuid4()),
            'Content-Type': 'application/json'
        }

    def get(self, path, query=None, **kwargs):
        query = query or []
        if 'page' in kwargs:
            query.append(('page', kwargs.get('page') or self.DEFAULT_PAGE_NUMBER))
        if 'page_size' in kwargs:
            query.append(('page-size', kwargs.get('page_size') or self.DEFAULT_PAGE_SIZE))

        url = self.endpoint + path + '?' + urlencode(query, doseq=True)
        try:
            response = self.session.get(url, headers=self.headers, auth=self.auth, timeout=self.timeout)
        except requests.exceptions.RequestException:
            raise
        return self._handle_error(response)

    def post(self, path, data=None):
        url = self.endpoint + path
        try:
            response = self.session.post(url, data=json.dumps(data, cls=CustomJsonEncoder),
                                         headers=self.headers, auth=self.auth, timeout=self.timeout)
        except requests.exceptions.RequestException:
            raise
        return self._handle_error(response)

    def put(self, path, data=None):
        url = self.endpoint + path
        try:
            response = self.session.put(url, data=json.dumps(data, cls=CustomJsonEncoder),
                                        headers=self.headers, auth=self.auth, timeout=self.timeout)
        except requests.exceptions.RequestException:
            raise
        return self._handle_error(response)

    def delete(self, path):
        url = self.endpoint + path

        try:
            response = self.session.delete(url, headers=self.headers, auth=self.auth, timeout=self.timeout)
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
