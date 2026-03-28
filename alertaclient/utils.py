from __future__ import annotations

import datetime
import json
import os
import platform
import sys
from typing import Any

import click
import pytz


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o: Any) -> str | int:  # pylint: disable=method-hidden
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S') + '.%03dZ' % (o.microsecond // 1000)
        elif isinstance(o, datetime.timedelta):
            return int(o.total_seconds())
        else:
            return json.JSONEncoder.default(self, o)


class DateTime:
    @staticmethod
    def parse(date_str: str | None) -> datetime.datetime | None:
        if not isinstance(date_str, str):
            return
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except Exception:
            raise ValueError('dates must be ISO 8601 date format YYYY-MM-DDThh:mm:ss.sssZ')

    @staticmethod
    def iso8601(dt: datetime.datetime) -> str:
        return dt.replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%S') + '.%03dZ' % (dt.microsecond // 1000)

    @staticmethod
    def localtime(dt: datetime.datetime | None, timezone: str | None = None, fmt: str = '%Y/%m/%d %H:%M:%S') -> str | None:
        tz = pytz.timezone(timezone)
        try:
            return dt.replace(tzinfo=pytz.UTC).astimezone(tz).strftime(fmt)
        except AttributeError:
            return


def build_query(filters: tuple[str, ...]) -> list[tuple[str, str]]:
    return [tuple(f.split('=', 1)) for f in filters if '=' in f]


def action_progressbar(client: Any, action: str, ids: list[str], label: str, text: str | None = None, timeout: int | None = None) -> None:
    skipped = 0

    def show_skipped(id: str | None) -> str | None:
        if not id and skipped:
            return f'(skipped {skipped})'

    with click.progressbar(ids, label=label, show_eta=True, item_show_func=show_skipped) as bar:
        for id in bar:
            try:
                client.action(id, action=action, text=text, timeout=timeout)
            except Exception:
                skipped += 1


def origin() -> str:
    prog = os.path.basename(sys.argv[0])
    return f'{prog}/{platform.uname()[1]}'
