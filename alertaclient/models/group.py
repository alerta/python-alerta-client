
from typing import Any, Dict
from uuid import uuid4

JSON = Dict[str, Any]


# class GroupUser:
#
#     def __init__(self, id: str, login: str, name: str, status: str) -> None:
#         self.id = id
#         self.login = login
#         self.name = name
#         self.status = status
#

# class GroupUsers:
#
#     def __init__(self, id: str, users: List[GroupUser]) -> None:
#         self.id = id
#         self.users = users


class Group:
    """
    Group model.
    """

    def __init__(self, name: str, text: str, **kwargs) -> None:
        if not name:
            raise ValueError('Missing mandatory value for name')

        self.id = kwargs.get('id', str(uuid4()))
        self.name = name
        self.text = text or ''
        self.count = kwargs.get('count')

    def __repr__(self) -> str:
        return 'Group(id={!r}, name={!r}, text={!r}, count={!r})'.format(
            self.id, self.name, self.text, self.count)

    @classmethod
    def parse(cls, json: JSON) -> 'Group':
        return Group(
            id=json.get('id', None),
            name=json.get('name', None),
            text=json.get('text', None),
            count=json.get('count', 0)
        )

    def tabular(self):
        return {
            'id': self.id,
            'name': self.name,
            'text': self.text,
            'count': self.count
        }
