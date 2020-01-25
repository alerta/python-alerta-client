from alertaclient.utils import DateTime


class ApiKey:

    def __init__(self, user, scopes, text='', expire_time=None, customer=None, **kwargs):
        self.id = kwargs.get('id', None)
        self.key = kwargs.get('key', None)
        self.user = user
        self.scopes = scopes
        self.text = text
        self.expire_time = expire_time
        self.count = kwargs.get('count', 0)
        self.last_used_time = kwargs.get('last_used_time', None)
        self.customer = customer

    @property
    def type(self):
        return self.scopes_to_type(self.scopes)

    def __repr__(self):
        return 'ApiKey(key={!r}, user={!r}, scopes={!r}, expireTime={!r}, customer={!r})'.format(
            self.key, self.user, self.scopes, self.expire_time, self.customer)

    @classmethod
    def parse(cls, json):
        if not isinstance(json.get('scopes', []), list):
            raise ValueError('scopes must be a list')

        return ApiKey(
            id=json.get('id', None),
            key=json.get('key', None),
            user=json.get('user', None),
            scopes=json.get('scopes', None) or list(),
            text=json.get('text', None),
            expire_time=DateTime.parse(json.get('expireTime')),
            count=json.get('count', None),
            last_used_time=DateTime.parse(json.get('lastUsedTime')),
            customer=json.get('customer', None)
        )

    def scopes_to_type(self, scopes):
        for scope in scopes:
            if scope.startswith('write') or scope.startswith('admin'):
                return 'read-write'
        return 'read-only'

    def tabular(self, timezone=None):
        return {
            'id': self.id,
            'key': self.key,
            'user': self.user,
            'scopes': ','.join(self.scopes),
            'text': self.text,
            'expireTime': DateTime.localtime(self.expire_time, timezone),
            'count': self.count,
            'lastUsedTime': DateTime.localtime(self.last_used_time, timezone),
            'customer': self.customer
        }
