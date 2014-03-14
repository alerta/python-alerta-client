
from json import JSONEncoder


class AlertEncoder(JSONEncoder):

    def default(self, o):

        return o.__dict__


class Alert(object):

    def __init__(self, resource, event, environment=None):

        if not resource:
            raise ValueError('Missing mandatory value for resource')
        if not event:
            raise ValueError('Missing mandatory value for event')

        self.resource = resource
        self.event = event
        self.environment = environment or 'production'

    def get(self):

        return {
            "resource": self.resource,
            "event": self.event,
            "environment": self.environment
        }

    def __repr__(self):

        return 'Alert(resource=%s, event=%s)' % (self.resource, self.event)

