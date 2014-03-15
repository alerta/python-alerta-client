
import json
import urllib
import requests

from alert import AlertEncoder
from heartbeat import HeartbeatEncoder


class ApiClient(object):

    def __init__(self, host='api.alerta.io', port=80, root='/api'):

        self.endpoint = 'http://%s:%s%s' % (host, port, root)

    def query(self, **kwargs):

        r = self._get('/alerts', kwargs)
        return r

    def send(self, alert):

        r = self._post('/alert', data=json.dumps(alert, cls=AlertEncoder))
        return r['receivedAlert']['_id']

    def show(self, alertid):

        r = self._get('/alert/%s' % alertid)
        return r

    def tag(self, alertid, tags):

        if not isinstance(tags, list):
            raise

        data = {"tags": tags}
        r = self._post('/alert/%s/tag' % alertid, data=json.dumps(data))
        return r['status']

    def open(self, alertid):

        self.status(alertid, 'open')

    def ack(self, alertid):

        self.status(alertid, 'ack')

    def unack(self, alertid):

        self.open(alertid)

    def assign(self, alertid):

        self.status(alertid, 'assigned')

    def close(self, alertid):

        self.status(alertid, 'closed')

    def status(self, alertid, status):

        data = {"status": status}
        r = self._post('/alert/%s/status' % alertid, data=json.dumps(data))
        return r['status']

    def delete(self, alertid):

        self._delete('/alert/%s' % alertid)

    def heartbeats(self):
        """
        Get list of heartbeats
        """
        r = self._get('/heartbeats')
        return r

    def heartbeat(self, heartbeat):
        """
        Send a heartbeat
        """
        r = self._post('/heartbeat', data=json.dumps(heartbeat, cls=HeartbeatEncoder))
        return r

    def _get(self, path, query=None):

        url = self.endpoint + path + urllib.urlencode(query)
        response = requests.get(url).json()

        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise

        return response.json()

    def _post(self, path, data=None):

        url = self.endpoint + path
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data, headers=headers)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise

        return response.json()

    def _delete(self, path):

        url = self.endpoint + path
        response = requests.delete(url)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise

        return response.json()
