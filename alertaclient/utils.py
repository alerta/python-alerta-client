
import datetime
import json

import click
import pytz
import six


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S') + '.%03dZ' % (o.microsecond // 1000)
        elif isinstance(o, datetime.timedelta):
            return int(o.total_seconds())
        else:
            return json.JSONEncoder.default(self, o)


class DateTime:
    @staticmethod
    def parse(date_str):
        if not isinstance(date_str, six.string_types):
            return
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except Exception:
            raise ValueError('dates must be ISO 8601 date format YYYY-MM-DDThh:mm:ss.sssZ')

    @staticmethod
    def iso8601(dt):
        return dt.replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S') + '.%03dZ' % (dt.microsecond // 1000)

    @staticmethod
    def localtime(dt, timezone=None, fmt='%Y/%m/%d %H:%M:%S'):
        tz = pytz.timezone(timezone)
        try:
            return dt.replace(tzinfo=pytz.UTC).astimezone(tz).strftime(fmt)
        except AttributeError:
            return


def build_query(filters):
    return [tuple(f.split('=', 1)) for f in filters if '=' in f]


def action_progressbar(client, action, ids, label, text=None, timeout=None):
    skipped = 0

    def show_skipped(id):
        if not id and skipped:
            return '(skipped {})'.format(skipped)

    with click.progressbar(ids, label=label, show_eta=True, item_show_func=show_skipped) as bar:
        for id in bar:
            try:
                client.action(id, action=action, text=text or 'status changed using CLI', timeout=timeout)
            except Exception as e:
                skipped += 1
