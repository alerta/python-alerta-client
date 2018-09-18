
from datetime import datetime, timedelta

from alertaclient.utils import DateTime

MAX_LATENCY = 2000  # ms


class Heartbeat:

    def __init__(self, origin=None, tags=None, create_time=None, timeout=None, customer=None, **kwargs):
        self.id = kwargs.get('id', None)
        self.origin = origin
        self.tags = tags or list()
        self.event_type = kwargs.get('event_type', kwargs.get('type', None)) or 'Heartbeat'
        self.create_time = create_time
        self.timeout = timeout
        self.receive_time = kwargs.get('receive_time', None)
        self.customer = customer

    @property
    def latency(self):
        return int((self.receive_time - self.create_time).total_seconds() * 1000)

    @property
    def since(self):
        since = datetime.utcnow() - self.receive_time
        return since - timedelta(microseconds=since.microseconds)

    @property
    def status(self):
        if self.latency > MAX_LATENCY:
            return 'slow'
        elif self.since.total_seconds() > self.timeout:
            return 'expired'  # aka 'stale'
        else:
            return 'ok'

    def __repr__(self):
        return 'Heartbeat(id={!r}, origin={!r}, create_time={!r}, timeout={!r}, customer={!r})'.format(
            self.id, self.origin, self.create_time, self.timeout, self.customer)

    @classmethod
    def parse(cls, json):
        if not isinstance(json.get('tags', []), list):
            raise ValueError('tags must be a list')
        if not isinstance(json.get('timeout', 0), int):
            raise ValueError('timeout must be an integer')

        return Heartbeat(
            id=json.get('id', None),
            origin=json.get('origin', None),
            tags=json.get('tags', list()),
            event_type=json.get('type', None),
            create_time=DateTime.parse(json.get('createTime')),
            timeout=json.get('timeout', None),
            receive_time=DateTime.parse(json.get('receiveTime')),
            customer=json.get('customer', None)
        )

    def tabular(self, timezone=None):
        return {
            'id': self.id,
            'origin': self.origin,
            'customer': self.customer,
            'tags': ','.join(self.tags),
            'createTime': DateTime.localtime(self.create_time, timezone),
            'receiveTime': DateTime.localtime(self.receive_time, timezone),
            'latency': '{:.0f}ms'.format(self.latency),
            'timeout': '{}s'.format(self.timeout),
            'since': self.since,
            'status': self.status
        }
