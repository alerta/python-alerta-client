
from json import JSONEncoder


class HeartbeatEncoder(JSONEncoder):

    def default(self, o):

        return o.__dict__


class Heartbeat(object):

    def __init__(self, origin):

        if not origin:
            raise ValueError('Missing mandatory value for origin')

        self.origin = origin

    def get(self):

        return {
            "origin": self.origin,
            "type": "Heartbeat"
        }

    def __repr__(self):

        return 'Heartbeat(origin=%s)' % self.origin

