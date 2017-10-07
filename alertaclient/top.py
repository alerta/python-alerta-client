
import curses
import sys
import time
from curses import wrapper
from datetime import datetime

from alertaclient.models.alert import Alert
from alertaclient.utils import DateTime


class Screen(object):

    ALIGN_RIGHT = 'R'
    ALIGN_CENTRE = 'C'

    def __init__(self, client):
        self.client = client

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
            'critical': ["Crit", COLOR_RED],
            'major': ["Majr", COLOR_MAGENTA],
            'minor': ["Minr", COLOR_YELLOW],
            'warning': ["Warn", COLOR_BLUE],
            'indeterminate': ["Ind ", COLOR_CYAN],
            'cleared': ["Clr", COLOR_GREEN],
            'normal': ["Norm", COLOR_GREEN],
            'inform': ["Info", COLOR_GREEN],
            'ok': ["Ok", COLOR_GREEN],
            'debug': ["Dbug", COLOR_BLACK],
            'auth': ["Sec", COLOR_BLACK],
            'unknown': ["Unkn", COLOR_BLACK]
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

        # draw bars

        # draw alerts
        self._addstr(2, 1, 'Sev. Time     Dupl. Env.         Service      Resource     Event        Value ', curses.A_UNDERLINE)

        def short_sev(severity):
            return self.SEVERITY_MAP[severity][0]

        def color(severity):
            return self.SEVERITY_MAP[severity][1]

        r = self.client.http.get('/alerts')
        alerts = [Alert.parse(a) for a in r['alerts']]
        last_time = DateTime.parse(r['lastTime'])
        for i, alert in enumerate(alerts):
            self._addstr(i+3, 1, '{0:<4} {1} {2:5d} {3:<12} {4:<12} {5:<12.12} {6:<12.12} {7:<6.6}'.format(
                short_sev(alert.severity),
                alert.last_receive_time.strftime('%H:%M:%S'),
                alert.duplicate_count,
                alert.environment,
                ','.join(alert.service),
                alert.resource,
                alert.event,
                alert.value
            ), color(alert.severity))

        # draw footer
        self._addstr(self.lines - 1, 0, 'Last Update: {}'.format(last_time.strftime('%H:%M:%S')), curses.A_BOLD)
        self._addstr(self.lines - 1, 'C', '{} - {}'.format(r['status'], r.get('message', 'no errors')), curses.A_BOLD)
        self._addstr(self.lines - 1, 'R', 'Count: {}'.format(r['total']), curses.A_BOLD)

        self.screen.refresh()

    def _addstr(self, y, x, str, attr=0):
        if x == self.ALIGN_RIGHT:
            x = self.cols - len(str) - 1
        if x == self.ALIGN_CENTRE:
            x = int((self.cols / 2) - len(str) / 2)

        self.screen.addstr(y, x, str, attr)

    def _key_press(self, key):
        if key in 'qQ':
            sys.exit(0)
