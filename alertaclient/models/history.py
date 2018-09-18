
from datetime import datetime

from alertaclient.utils import DateTime


class History:

    def __init__(self, id, event, **kwargs):
        self.id = id
        self.event = event
        self.severity = kwargs.get('severity', None)
        self.status = kwargs.get('status', None)
        self.value = kwargs.get('value', None)
        self.change_type = kwargs.get('change_type', kwargs.get('type', None)) or ''
        self.text = kwargs.get('text', None)
        self.update_time = kwargs.get('update_time', None) or datetime.utcnow()

    def __repr__(self):
        return 'History(id={!r}, event={!r}, severity={!r}, status={!r}, type={!r})'.format(
            self.id, self.event, self.severity, self.status, self.change_type)


class RichHistory:

    def __init__(self, resource, event, **kwargs):

        self.id = kwargs.get('id', None)
        self.resource = resource
        self.event = event
        self.environment = kwargs.get('environment', None)
        self.severity = kwargs.get('severity', None)
        self.status = kwargs.get('status', None)
        self.service = kwargs.get('service', None) or list()
        self.group = kwargs.get('group', None)
        self.value = kwargs.get('value', None)
        self.text = kwargs.get('text', None)
        self.tags = kwargs.get('tags', None) or list()
        self.attributes = kwargs.get('attributes', None) or dict()
        self.origin = kwargs.get('origin', None)
        self.update_time = kwargs.get('update_time', None)
        self.change_type = kwargs.get('change_type', kwargs.get('type', None))
        self.customer = kwargs.get('customer', None)

    def __repr__(self):
        return 'RichHistory(id={!r}, environment={!r}, resource={!r}, event={!r}, severity={!r}, status={!r}, type={!r}, customer={!r})'.format(
            self.id, self.environment, self.resource, self.event, self.severity, self.status, self.change_type, self.customer)

    @classmethod
    def parse(cls, json):
        if not isinstance(json.get('service', []), list):
            raise ValueError('service must be a list')
        if not isinstance(json.get('tags', []), list):
            raise ValueError('tags must be a list')

        return RichHistory(
            id=json.get('id', None),
            resource=json.get('resource', None),
            event=json.get('event', None),
            environment=json.get('environment', None),
            severity=json.get('severity', None),
            status=json.get('status', None),
            service=json.get('service', list()),
            group=json.get('group', None),
            value=json.get('value', None),
            text=json.get('text', None),
            tags=json.get('tags', list()),
            attributes=json.get('attributes', dict()),
            origin=json.get('origin', None),
            change_type=json.get('type', None),
            update_time=DateTime.parse(json.get('updateTime')),
            customer=json.get('customer', None)
        )

    def tabular(self, timezone=None):
        data = {
            'id': self.id,
            'resource': self.resource,
            'event': self.event,
            'environment': self.environment,
            'service': ','.join(self.service),
            'group': self.group,
            'text': self.text,
            # 'tags': ','.join(self.tags),  # not displayed
            # 'attributes': self.attributes,
            # 'origin': self.origin,
            'type': self.change_type,
            'updateTime': DateTime.localtime(self.update_time, timezone),
            'customer': self.customer
        }

        if self.severity:
            data['severity'] = self.severity
            data['value'] = self.value

        if self.status:
            data['status'] = self.status

        return data
