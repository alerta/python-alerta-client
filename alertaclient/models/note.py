from datetime import datetime

from alertaclient.utils import DateTime


class Note:

    def __init__(self, text, user, note_type, **kwargs):

        self.id = kwargs.get('id', None)
        self.text = text
        self.user = user
        self.note_type = note_type
        self.attributes = kwargs.get('attributes', None) or dict()
        self.create_time = kwargs['create_time'] if 'create_time' in kwargs else datetime.utcnow()
        self.update_time = kwargs.get('update_time')
        self.alert = kwargs.get('alert')
        self.customer = kwargs.get('customer')

    @classmethod
    def parse(cls, json):
        return Note(
            id=json.get('id', None),
            text=json.get('text', None),
            user=json.get('user', None),
            attributes=json.get('attributes', dict()),
            note_type=json.get('type', None),
            create_time=DateTime.parse(json['createTime']) if 'createTime' in json else None,
            update_time=DateTime.parse(json['updateTime']) if 'updateTime' in json else None,
            alert=json.get('related', {}).get('alert'),
            customer=json.get('customer', None)
        )

    def __repr__(self):
        return 'Note(id={!r}, text={!r}, user={!r}, type={!r}, customer={!r})'.format(
            self.id, self.text, self.user, self.note_type, self.customer
        )

    def tabular(self, timezone=None):
        note = {
            'id': self.id,
            'text': self.text,
            'createTime': DateTime.localtime(self.create_time, timezone),
            'user': self.user,
            # 'attributes': self.attributes,
            'type': self.note_type,
            'related': self.alert,
            'updateTime': DateTime.localtime(self.update_time, timezone),
            'customer': self.customer
        }
        return note
