from datetime import datetime, timedelta

from alertaclient.utils import DateTime


class Blackout:

    def __init__(self, environment, **kwargs):
        if not environment:
            raise ValueError('Missing mandatory value for "environment"')

        start_time = kwargs.get('start_time', None) or datetime.utcnow()
        if kwargs.get('end_time', None):
            end_time = kwargs.get('end_time')
            duration = int((end_time - start_time).total_seconds())
        else:
            duration = kwargs.get('duration', None)
            end_time = start_time + timedelta(seconds=duration)

        self.id = kwargs.get('id', None)
        self.environment = environment
        self.service = kwargs.get('service', None) or list()
        self.resource = kwargs.get('resource', None)
        self.event = kwargs.get('event', None)
        self.group = kwargs.get('group', None)
        self.tags = kwargs.get('tags', None) or list()
        self.origin = kwargs.get('origin', None)
        self.customer = kwargs.get('customer', None)
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration

        self.user = kwargs.get('user', None)
        self.create_time = kwargs.get('create_time', None)
        self.text = kwargs.get('text', None)

        if self.environment:
            self.priority = 1
        if self.resource and not self.event:
            self.priority = 2
        elif self.service:
            self.priority = 3
        elif self.event and not self.resource:
            self.priority = 4
        elif self.group:
            self.priority = 5
        elif self.resource and self.event:
            self.priority = 6
        elif self.tags:
            self.priority = 7
        if self.origin:
            self.priority = 8

        now = datetime.utcnow()
        if self.start_time <= now and self.end_time > now:
            self.status = 'active'
            self.remaining = int((self.end_time - now).total_seconds())
        elif self.start_time > now:
            self.status = 'pending'
            self.remaining = self.duration
        elif self.end_time <= now:
            self.status = 'expired'
            self.remaining = 0

    def __repr__(self):
        more = ''
        if self.service:
            more += 'service=%r, ' % self.service
        if self.resource:
            more += 'resource=%r, ' % self.resource
        if self.event:
            more += 'event=%r, ' % self.event
        if self.group:
            more += 'group=%r, ' % self.group
        if self.tags:
            more += 'tags=%r, ' % self.tags
        if self.origin:
            more += 'origin=%r, ' % self.origin
        if self.customer:
            more += 'customer=%r, ' % self.customer

        return 'Blackout(id={!r}, priority={!r}, status={!r}, environment={!r}, {}start_time={!r}, end_time={!r}, remaining={!r})'.format(
            self.id,
            self.priority,
            self.status,
            self.environment,
            more,
            self.start_time,
            self.end_time,
            self.remaining
        )

    @classmethod
    def parse(cls, json):
        if not isinstance(json.get('service', []), list):
            raise ValueError('service must be a list')
        if not isinstance(json.get('tags', []), list):
            raise ValueError('tags must be a list')

        return Blackout(
            id=json.get('id'),
            environment=json.get('environment'),
            service=json.get('service', list()),
            resource=json.get('resource', None),
            event=json.get('event', None),
            group=json.get('group', None),
            tags=json.get('tags', list()),
            origin=json.get('origin', None),
            customer=json.get('customer', None),
            start_time=DateTime.parse(json.get('startTime')),
            end_time=DateTime.parse(json.get('endTime')),
            duration=json.get('duration', None),
            user=json.get('user', None),
            create_time=DateTime.parse(json.get('createTime')),
            text=json.get('text', None)
        )

    def tabular(self, timezone=None):
        return {
            'id': self.id,
            'priority': self.priority,
            'environment': self.environment,
            'service': ','.join(self.service),
            'resource': self.resource,
            'event': self.event,
            'group': self.group,
            'tags': ','.join(self.tags),
            'origin': self.origin,
            'customer': self.customer,
            'startTime': DateTime.localtime(self.start_time, timezone),
            'endTime': DateTime.localtime(self.end_time, timezone),
            'duration': '{}s'.format(self.duration),
            'status': self.status,
            'remaining': '{}s'.format(self.remaining),
            'user': self.user,
            'createTime': DateTime.localtime(self.create_time, timezone),
            'text': self.text
        }
