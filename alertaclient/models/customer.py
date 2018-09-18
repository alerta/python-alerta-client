
class Customer:

    def __init__(self, match, customer, **kwargs):
        self.id = kwargs.get('id', None)
        self.match = match
        self.customer = customer

    def __repr__(self):
        return 'Customer(id={!r}, match={!r}, customer={!r})'.format(
            self.id, self.match, self.customer)

    @classmethod
    def parse(cls, json):
        return Customer(
            id=json.get('id', None),
            match=json.get('match', None),
            customer=json.get('customer', None)
        )

    def tabular(self):
        return {
            'id': self.id,
            'match': self.match,
            'customer': self.customer
        }
