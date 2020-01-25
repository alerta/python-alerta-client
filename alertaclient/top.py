import curses
import sys
import time
from curses import wrapper
from datetime import datetime

from alertaclient.models.alert import Alert
from alertaclient.utils import DateTime


class Screen:

    ALIGN_RIGHT = 'R'
    ALIGN_CENTRE = 'C'

    def __init__(self, client, timezone):
        self.client = client
        self.timezone = timezone

        self.screen = None
        self.lines = None
        self.cols = None

    def run(self):
        wrapper(self.main)

    def main(self, stdscr):
        self.screen = stdscr

        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_MAGENTA, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        curses.init_pair(6, curses.COLOR_GREEN, -1)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

        COLOR_RED = curses.color_pair(1)
        COLOR_MAGENTA = curses.color_pair(2)
        COLOR_YELLOW = curses.color_pair(3)
        COLOR_BLUE = curses.color_pair(4)
        COLOR_CYAN = curses.color_pair(5)
        COLOR_GREEN = curses.color_pair(6)
        COLOR_BLACK = curses.color_pair(7)

        self.SEVERITY_MAP = {
            'security': ['Sec', COLOR_BLACK],
            'critical': ['Crit', COLOR_RED],
            'major': ['Majr', COLOR_MAGENTA],
            'minor': ['Minr', COLOR_YELLOW],
            'warning': ['Warn', COLOR_BLUE],
            'indeterminate': ['Ind ', COLOR_CYAN],
            'cleared': ['Clr', COLOR_GREEN],
            'normal': ['Norm', COLOR_GREEN],
            'ok': ['Ok', COLOR_GREEN],
            'informational': ['Info', COLOR_GREEN],
            'debug': ['Dbug', COLOR_BLACK],
            'trace': ['Trce', COLOR_BLACK],
            'unknown': ['Unkn', COLOR_BLACK]
        }

        self.screen.keypad(1)
        self.screen.nodelay(1)

        while True:
            self.update()
            event = self.screen.getch()
            if 0 < event < 256:
                self._key_press(chr(event))
            else:
                if event == curses.KEY_RESIZE:
                    self.update()
            time.sleep(2)

    def update(self):
        self.lines, self.cols = self.screen.getmaxyx()
        self.screen.clear()

        now = datetime.utcnow()
        status = self.client.mgmt_status()
        version = status['version']

        # draw header
        self._addstr(0, 0, self.client.endpoint, curses.A_BOLD)
        self._addstr(0, 'C', 'alerta {}'.format(version), curses.A_BOLD)
        self._addstr(0, 'R', '{}'.format(now.strftime('%H:%M:%S %d/%m/%y')), curses.A_BOLD)

        # TODO - draw bars

        # draw alerts
        text_width = self.cols - 95 if self.cols >= 95 else 0
        self._addstr(2, 1, 'Sev. Time     Dupl. Customer Env.         Service      Resource     Group Event'
                     + '        Value Text' + ' ' * (text_width - 4), curses.A_UNDERLINE)

        def short_sev(severity):
            return self.SEVERITY_MAP.get(severity, self.SEVERITY_MAP['unknown'])[0]

        def color(severity):
            return self.SEVERITY_MAP.get(severity, self.SEVERITY_MAP['unknown'])[1]

        r = self.client.http.get('/alerts')
        alerts = [Alert.parse(a) for a in r['alerts']]
        last_time = DateTime.parse(r['lastTime'])

        for i, alert in enumerate(alerts):
            row = i + 3
            if row >= self.lines - 2:  # leave room for footer
                break

            text = '{:<4} {} {:5d} {:8.8} {:<12} {:<12} {:<12.12} {:5.5} {:<12.12} {:<5.5} {:.{width}}'.format(
                short_sev(alert.severity),
                DateTime.localtime(alert.last_receive_time, self.timezone, fmt='%H:%M:%S'),
                alert.duplicate_count,
                alert.customer or '-',
                alert.environment,
                ','.join(alert.service),
                alert.resource,
                alert.group,
                alert.event,
                alert.value or 'n/a',
                alert.text,
                width=text_width
            )
            # XXX - needed to support python2 and python3
            if not isinstance(text, str):
                text = text.encode('ascii', errors='replace')

            self._addstr(row, 1, text, color(alert.severity))

        # draw footer
        self._addstr(self.lines - 1, 0, 'Last Update: {}'.format(last_time.strftime('%H:%M:%S')), curses.A_BOLD)
        self._addstr(self.lines - 1, 'C', '{} - {}'.format(r['status'], r.get('message', 'no errors')), curses.A_BOLD)
        self._addstr(self.lines - 1, 'R', 'Count: {}'.format(r['total']), curses.A_BOLD)

        self.screen.refresh()

    def _addstr(self, y, x, line, attr=0):
        if x == self.ALIGN_RIGHT:
            x = self.cols - len(line) - 1
        if x == self.ALIGN_CENTRE:
            x = int((self.cols / 2) - len(line) / 2)

        self.screen.addstr(y, x, line, attr)

    def _key_press(self, key):
        if key in 'qQ':
            sys.exit(0)
