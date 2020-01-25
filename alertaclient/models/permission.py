class Permission:

    def __init__(self, match, scopes, **kwargs):
        self.id = kwargs.get('id', None)
        self.match = match
        self.scopes = scopes or list()

    def __repr__(self):
        return 'Perm(id={!r}, match={!r}, scopes={!r})'.format(
            self.id, self.match, self.scopes)

    @classmethod
    def parse(cls, json):
        if not isinstance(json.get('scopes', []), list):
            raise ValueError('scopes must be a list')

        return Permission(
            id=json.get('id', None),
            match=json.get('match', None),
            scopes=json.get('scopes', list())
        )

    def tabular(self):
        return {
            'id': self.id,
            'match': self.match,
            'scopes': ','.join(self.scopes)
        }
