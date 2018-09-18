
from alertaclient.utils import DateTime


class User:
    """
    User model for BasicAuth only.
    """

    def __init__(self, name, email, roles, text, **kwargs):
        self.id = kwargs.get('id', None)
        self.name = name
        self.email = email
        self.status = kwargs.get('status', None) or 'active'  # 'active', 'inactive', 'unknown'
        self.roles = roles
        self.attributes = kwargs.get('attributes', None) or dict()
        self.create_time = kwargs.get('create_time', None)
        self.last_login = kwargs.get('last_login', None)
        self.text = text or ''
        self.update_time = kwargs.get('update_time', None)
        self.email_verified = kwargs.get('email_verified', False)

    @property
    def domain(self):
        return self.email.split('@')[1] if '@' in self.email else None

    def __repr__(self):
        return 'User(id={!r}, name={!r}, email={!r}, status={!r}, roles={!r}, email_verified={!r})'.format(
            self.id, self.name, self.email, self.status, ','.join(self.roles), self.email_verified
        )

    @classmethod
    def parse(cls, json):
        return User(
            id=json.get('id'),
            name=json.get('name'),
            email=json.get('email', None) or json.get('login'),
            status=json.get('status'),
            roles=json.get('roles', None) or ([json['role']] if 'role' in json else list()),
            attributes=json.get('attributes', dict()),
            create_time=DateTime.parse(json.get('createTime')),
            last_login=DateTime.parse(json.get('lastLogin')),
            text=json.get('text', None),
            update_time=DateTime.parse(json.get('updateTime')),
            email_verified=json.get('email_verified', None)
        )

    def tabular(self, timezone=None):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'status': self.status,
            'roles': ','.join(self.roles),
            # 'attributes': self.attributes,  # reserved for future use
            'createTime': DateTime.localtime(self.create_time, timezone),
            'lastLogin': DateTime.localtime(self.last_login, timezone),
            'text': self.text,
            'updateTime': DateTime.localtime(self.update_time, timezone),
            'email_verified': 'yes' if self.email_verified else 'no'
        }
