from datetime import datetime, timedelta

from alertaclient.utils import DateTime

DEFAULT_MAX_LATENCY = 2000  # ms


class Heartbeat:

    def __init__(self, origin=None, tags=None, create_time=None, timeout=None, customer=None, **kwargs):
        if any(['.' in key for key in kwargs.get('attributes', dict()).keys()])\
                or any(['$' in key for key in kwargs.get('attributes', dict()).keys()]):
            raise ValueError('Attribute keys must not contain "." or "$"')

        self.id = kwargs.get('id', None)
        self.origin = origin
        self.status = kwargs.get('status', None) or 'unknown'
        self.tags = tags or list()
        self.attributes = kwargs.get('attributes', None) or dict()
        self.event_type = kwargs.get('event_type', kwargs.get('type', None)) or 'Heartbeat'
        self.create_time = create_time
        self.timeout = timeout
        self.max_latency = kwargs.get('max_latency', None) or DEFAULT_MAX_LATENCY
        self.receive_time = kwargs.get('receive_time', None)
        self.customer = customer

    @property
    def latency(self):
        return int((self.receive_time - self.create_time).total_seconds() * 1000)

    @property
    def since(self):
        since = datetime.utcnow() - self.receive_time
        return since - timedelta(microseconds=since.microseconds)

    def __repr__(self):
        return 'Heartbeat(id={!r}, origin={!r}, create_time={!r}, timeout={!r}, customer={!r})'.format(
            self.id, self.origin, self.create_time, self.timeout, self.customer)

    @classmethod
    def parse(cls, json):
        if not isinstance(json.get('tags', []), list):
            raise ValueError('tags must be a list')
        if not isinstance(json.get('attributes', {}), dict):
            raise ValueError('attributes must be a JSON object')
        if not isinstance(json.get('timeout', 0), int):
            raise ValueError('timeout must be an integer')

        return Heartbeat(
            id=json.get('id', None),
            origin=json.get('origin', None),
            status=json.get('status', None),
            tags=json.get('tags', list()),
            attributes=json.get('attributes', dict()),
            event_type=json.get('type', None),
            create_time=DateTime.parse(json.get('createTime')),
            timeout=json.get('timeout', None),
            max_latency=json.get('maxLatency', None) or DEFAULT_MAX_LATENCY,
            receive_time=DateTime.parse(json.get('receiveTime')),
            customer=json.get('customer', None)
        )

    def tabular(self, timezone=None):
        return {
            'id': self.id,
            'origin': self.origin,
            'customer': self.customer,
            'tags': ','.join(self.tags),
            'attributes': self.attributes,
            'createTime': DateTime.localtime(self.create_time, timezone),
            'receiveTime': DateTime.localtime(self.receive_time, timezone),
            'since': self.since,
            'timeout': '{}s'.format(self.timeout),
            'latency': '{:.0f}ms'.format(self.latency),
            'maxLatency': '{}ms'.format(self.max_latency),
            'status': self.status
        }
