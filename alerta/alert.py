
class Alert(object):

    def __init__(self, resource, event):

        if not resource:
            raise ValueError('Missing mandatory value for resource')
        if not event:
            raise ValueError('Missing mandatory value for event')

        self.resource = resource
        self.event = event
