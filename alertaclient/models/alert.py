
from datetime import datetime

from alertaclient.utils import DateTime


class Alert:

    def __init__(self, resource, event, **kwargs):
        if not resource:
            raise ValueError('Missing mandatory value for "resource"')
        if not event:
            raise ValueError('Missing mandatory value for "event"')
        if any(['.' in key for key in kwargs.get('attributes', dict()).keys()])\
                or any(['$' in key for key in kwargs.get('attributes', dict()).keys()]):
            raise ValueError('Attribute keys must not contain "." or "$"')

        self.id = kwargs.get('id', None)
        self.resource = resource
        self.event = event
        self.environment = kwargs.get('environment', None) or ''
        self.severity = kwargs.get('severity', None)
        self.correlate = kwargs.get('correlate', None) or list()
        if self.correlate and event not in self.correlate:
            self.correlate.append(event)
        self.status = kwargs.get('status', None) or 'unknown'
        self.service = kwargs.get('service', None) or list()
        self.group = kwargs.get('group', None) or 'Misc'
        self.value = kwargs.get('value', None)
        self.text = kwargs.get('text', None) or ''
        self.tags = kwargs.get('tags', None) or list()
        self.attributes = kwargs.get('attributes', None) or dict()
        self.origin = kwargs.get('origin', None)
        self.event_type = kwargs.get('event_type', kwargs.get('type', None)) or 'exceptionAlert'
        self.create_time = kwargs.get('create_time', None) or datetime.utcnow()
        self.timeout = kwargs.get('timeout', None)
        self.raw_data = kwargs.get('raw_data', None)
        self.customer = kwargs.get('customer', None)

        self.duplicate_count = kwargs.get('duplicate_count', None)
        self.repeat = kwargs.get('repeat', None)
        self.previous_severity = kwargs.get('previous_severity', None)
        self.trend_indication = kwargs.get('trend_indication', None)
        self.receive_time = kwargs.get('receive_time', None) or datetime.utcnow()
        self.last_receive_id = kwargs.get('last_receive_id', None)
        self.last_receive_time = kwargs.get('last_receive_time', None)
        self.history = kwargs.get('history', None) or list()

    def __repr__(self):
        return 'Alert(id={!r}, environment={!r}, resource={!r}, event={!r}, severity={!r}, status={!r}, customer={!r})'.format(
            self.id, self.environment, self.resource, self.event, self.severity, self.status, self.customer)

    @classmethod
    def parse(cls, json):
        if not isinstance(json.get('correlate', []), list):
            raise ValueError('correlate must be a list')
        if not isinstance(json.get('service', []), list):
            raise ValueError('service must be a list')
        if not isinstance(json.get('tags', []), list):
            raise ValueError('tags must be a list')
        if not isinstance(json.get('attributes', {}), dict):
            raise ValueError('attributes must be a JSON object')
        if not isinstance(json.get('timeout') if json.get('timeout', None) is not None else 0, int):
            raise ValueError('timeout must be an integer')

        return Alert(
            id=json.get('id', None),
            resource=json.get('resource', None),
            event=json.get('event', None),
            environment=json.get('environment', None),
            severity=json.get('severity', None),
            correlate=json.get('correlate', list()),
            status=json.get('status', None),
            service=json.get('service', list()),
            group=json.get('group', None),
            value=json.get('value', None),
            text=json.get('text', None),
            tags=json.get('tags', list()),
            attributes=json.get('attributes', dict()),
            origin=json.get('origin', None),
            event_type=json.get('type', None),
            create_time=DateTime.parse(json.get('createTime')),
            timeout=json.get('timeout', None),
            raw_data=json.get('rawData', None),
            customer=json.get('customer', None),

            duplicate_count=json.get('duplicateCount', None),
            repeat=json.get('repeat', None),
            previous_severity=json.get('previousSeverity', None),
            trend_indication=json.get('trendIndication', None),
            receive_time=DateTime.parse(json.get('receiveTime')),
            last_receive_id=json.get('lastReceiveId', None),
            last_receive_time=DateTime.parse(json.get('lastReceiveTime')),
            history=json.get('history', None)
        )

    def get_id(self, short=False):
        return self.id[:8] if short else self.id

    def tabular(self, fields='all', timezone=None):
        if fields == 'summary':
            return {
                'id': self.get_id(short=True),
                'lastReceiveTime': DateTime.localtime(self.last_receive_time, timezone),
                'severity': self.severity,
                'status': self.status,
                'duplicateCount': self.duplicate_count,
                'customer': self.customer,
                'environment': self.environment,
                'service': ','.join(self.service),
                'resource': self.resource,
                'group': self.group,
                'event': self.event,
                'value': self.value,
                'text': self.text
            }
        elif fields == 'details':
            return {
                'severity': '{} -> {}'.format(self.previous_severity, self.severity),
                'trend': self.trend_indication,
                'status': self.status,
                'resource': self.resource,
                'group': self.group,
                'event': self.event,
                'value': self.value,
                'tags': ','.join(self.tags)
            }
        else:
            return {
                'id': self.id,
                'resource': self.resource,
                'event': self.event,
                'environment': self.environment,
                'severity': self.severity,
                'correlate': self.correlate,
                'status': self.status,
                'service': ','.join(self.service),
                'group': self.group,
                'value': self.value,
                'text': self.text,
                'tags': ','.join(self.tags),
                'attributes': self.attributes,
                'origin': self.origin,
                'type': self.event_type,
                'createTime': DateTime.localtime(self.create_time, timezone),
                'timeout': self.timeout,
                'rawData': self.raw_data,
                'customer': self.customer,
                'duplicateCount': self.duplicate_count,
                'repeat': self.repeat,
                'previousSeverity': self.previous_severity,
                'trendIndication': self.trend_indication,
                'receiveTime': DateTime.localtime(self.receive_time, timezone),
                'lastReceiveId': self.last_receive_id,
                'lastReceiveTime': DateTime.localtime(self.last_receive_time, timezone),
                'history': self.history
            }
