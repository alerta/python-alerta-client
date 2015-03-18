
import os
import json
import urllib
import requests
import logging

from requests.auth import AuthBase

LOG = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 86400


class ApiAuth(AuthBase):

    def __init__(self, key):

        self.key = key

    def __call__(self, r):

        r.headers['Authorization'] = 'Key %s' % self.key
        return r


class ApiClient(object):

    def __init__(self, endpoint=None, key=None):

        self.endpoint = endpoint or os.environ.get('ALERTA_ENDPOINT', "http://localhost:8080")
        self.key = key or os.environ.get('ALERTA_API_KEY', '')
        self.session = requests.Session()

    def __repr__(self):

        return 'ApiClient(endpoint=%r, key=%r)' % (self.endpoint, self.key)

    def get_alerts(self, query):

        return self._get('/alerts', query)

    def get_counts(self, query):

        return self._get('/alerts/count', query)

    def get_history(self, query):

        return self._get('/alerts/history', query)

    def send_alert(self, alert):

        return self._post('/alert', data=str(alert))

    def send(self, msg):

        if msg.event_type == 'Heartbeat':
            return self.send_heartbeat(msg)
        else:
            return self.send_alert(msg)

    def get_alert(self, alertid):

        return self._get('/alert/%s' % alertid)

    def tag_alert(self, alertid, tags):

        if not isinstance(tags, list):
            raise

        return self._post('/alert/%s/tag' % alertid, data=json.dumps({"tags": tags}))

    def untag_alert(self, alertid, tags):

        if not isinstance(tags, list):
            raise

        return self._post('/alert/%s/untag' % alertid, data=json.dumps({"tags": tags}))

    def open_alert(self, alertid):

        self.update_status(alertid, 'open')

    def ack_alert(self, alertid):

        self.update_status(alertid, 'ack')

    def unack_alert(self, alertid):

        self.open_alert(alertid)

    def assign_alert(self, alertid):

        self.update_status(alertid, 'assigned')

    def close_alert(self, alertid):

        self.update_status(alertid, 'closed')

    def update_status(self, alertid, status):

        return self._post('/alert/%s/status' % alertid, data=json.dumps({"status": status}))

    def delete_alert(self, alertid):

        return self._delete('/alert/%s' % alertid)

    def send_heartbeat(self, heartbeat):
        """
        Send a heartbeat
        """
        return self._post('/heartbeat', data=str(heartbeat))

    def get_heartbeats(self):
        """
        Get list of heartbeats
        """
        return self._get('/heartbeats')

    def delete_heartbeat(self, heartbeatid):

        return self._delete('/heartbeat/%s' % heartbeatid)

    def get_status(self):

        return self._get('/management/status')

    def _get(self, path, query=None):

        query = query or tuple()

        url = self.endpoint + path + '?' + urllib.urlencode(query, doseq=True)
        response = self.session.get(url, auth=ApiAuth(self.key))

        LOG.debug('Content type from response: %s', response.headers['content-type'])
        LOG.debug('Response Headers: %s', response.headers)
        LOG.debug('Response Body: %s', response.text)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise

        return response.json()

    def _post(self, path, data=None):

        url = self.endpoint + path
        headers = {'Content-Type': 'application/json'}

        LOG.debug('Request Headers: %s', headers)
        LOG.debug('Request Body: %s', data)

        response = self.session.post(url, data=data, auth=ApiAuth(self.key), headers=headers)

        return response.json()

    def _delete(self, path):

        url = self.endpoint + path
        response = self.session.delete(url, auth=ApiAuth(self.key))

        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise

        return response.json()
