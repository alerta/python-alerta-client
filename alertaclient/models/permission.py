from __future__ import annotations

from typing import Any

JSON = dict[str, Any]


class Permission:

    def __init__(self, match: str, scopes: list[str] | None, **kwargs: Any) -> None:
        self.id = kwargs.get('id', None)
        self.match = match
        self.scopes = scopes or list()

    def __repr__(self) -> str:
        return 'Perm(id={!r}, match={!r}, scopes={!r})'.format(
            self.id, self.match, self.scopes)

    @classmethod
    def parse(cls, json: JSON) -> Permission:
        if not isinstance(json.get('scopes', []), list):
            raise ValueError('scopes must be a list')

        return Permission(
            id=json.get('id', None),
            match=json.get('match', None),
            scopes=json.get('scopes', list())
        )

    def tabular(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'match': self.match,
            'scopes': ','.join(self.scopes)
        }
