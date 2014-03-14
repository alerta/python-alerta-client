
import json
import urllib
import requests

from alert import AlertEncoder
from heartbeat import HeartbeatEncoder


class ApiClient(object):

    def __init__(self, host='api.alerta.io', port=80, root='/api'):

        self.endpoint = 'http://%s:%s%s' % (host, port, root)

    def query(self):

        pass

    def send(self, data):

        r = self._post('/alert', data=json.dumps(data, cls=AlertEncoder))
        return r['receivedAlert']['_id']

    def open(self, alertid):

        self.update_status(alertid, 'open')

    def ack(self, alertid):

        self.update_status(alertid, 'ack')

    def unack(self, alertid):

        self.open(alertid)

    def assign(self, alertid):

        self.update_status(alertid, 'assigned')

    def close(self, alertid):

        self.update_status(alertid, 'closed')

    def update_status(self, alertid, status):

        data = {"status": status}
        r = self._post('/alert/%s/status' % alertid, data=json.dumps(data))
        return r['status']

    def tag(self, alertid, tags):

        if not isinstance(tags, list):
            raise

        data = {"tags": tags}
        r = self._post('/alert/%s/tag' % alertid, data=json.dumps(data))
        return r['status']

    def delete(self, alertid):

        self._delete('/alert', alertid)

    def _get(self, path, filter=[]):

        url = self.endpoint + path + '?_expand&' + urllib.urlencode(filter)
        response = requests.get(url).json()

        return response

    def _post(self, path, data=None):

        url = self.endpoint + path
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data, headers=headers)

        print url
        print data
        print response
        print response.text

        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise

        return response.json()

    def _delete(self, path, alertid):

        url = self.endpoint + path + '/' + alertid
        response = requests.delete(url)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise

        return response.json()
