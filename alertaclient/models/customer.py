from __future__ import annotations

from typing import Any

JSON = dict[str, Any]


class Customer:

    def __init__(self, match: str, customer: str, **kwargs: Any) -> None:
        self.id = kwargs.get('id', None)
        self.match = match
        self.customer = customer

    def __repr__(self) -> str:
        return 'Customer(id={!r}, match={!r}, customer={!r})'.format(
            self.id, self.match, self.customer)

    @classmethod
    def parse(cls, json: JSON) -> Customer:
        return Customer(
            id=json.get('id', None),
            match=json.get('match', None),
            customer=json.get('customer', None)
        )

    def tabular(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'match': self.match,
            'customer': self.customer
        }
