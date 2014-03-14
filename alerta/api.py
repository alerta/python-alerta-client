
import urllib
import requests


class ApiClient(object):

    def __init__(self, host='api.alerta.io', port=80):

        self.endpoint = 'http://%s:%s' % (host, port)

    def query(self):

        pass

    def send(self, **kwargs):

        uuid = self._post('/alert', kwargs)
        return uuid

    def send_hearbeat(self, heartbeat):

        pass

    def ack(self):

        pass

    def delete(self):

        pass

    def _get(self, path, filter=[]):

        url = self.endpoint + path + '?_expand&' + urllib.urlencode(filter)
        response = requests.get(url).json()

        return response

    def _post(self, path, data=None):

        url = self.endpoint + path + urllib.urlencode(filter)
        response = requests.post(url, data=data).json()

        return response