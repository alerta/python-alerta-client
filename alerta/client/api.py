
import json
import urllib
import requests
import logging

LOG = logging.getLogger(__name__)


class ApiClient(object):

    def __init__(self, endpoint):

        self.endpoint = endpoint

    def __repr__(self):

        return 'ApiClient(endpoint=%r)' % self.endpoint

    def get_alerts(self, **kwargs):

        return self._get('/alerts', kwargs)

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

    def _get(self, path, query=None):

        url = self.endpoint + path + '?' + urllib.urlencode(query)
        response = requests.get(url)

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
