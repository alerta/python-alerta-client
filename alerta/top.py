
import sys
import time
import curses
import threading
import signal
import copy

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from datetime import datetime
from requests import ConnectionError

from alerta.api import ApiClient
from alerta.alert import AlertDocument

SCREEN_REDRAW_INTERVAL = 2
lock = threading.Lock()


CRITICAL_SEV_CODE = 1
MAJOR_SEV_CODE = 2
MINOR_SEV_CODE = 3
WARNING_SEV_CODE = 4
INDETER_SEV_CODE = 5
CLEARED_SEV_CODE = 5
NORMAL_SEV_CODE = 5
OK_SEV_CODE = 5
INFORM_SEV_CODE = 6
DEBUG_SEV_CODE = 7
AUTH_SEV_CODE = 8
UNKNOWN_SEV_CODE = 9

# NOTE: The display text in single quotes can be changed depending on preference.
# eg. CRITICAL = 'critical' or CRITICAL = 'CRITICAL'

CRITICAL = 'critical'
MAJOR = 'major'
MINOR = 'minor'
WARNING = 'warning'
INDETERMINATE = 'indeterminate'
CLEARED = 'cleared'
NORMAL = 'normal'
OK = 'ok'
INFORM = 'informational'
DEBUG = 'debug'
AUTH = 'security'
UNKNOWN = 'unknown'
NOT_VALID = 'notValid'

ALL = [CRITICAL, MAJOR, MINOR, WARNING, INDETERMINATE, CLEARED, NORMAL, OK, INFORM, DEBUG, AUTH, UNKNOWN, NOT_VALID]

_SEVERITY_MAP = {
    CRITICAL: CRITICAL_SEV_CODE,
    MAJOR: MAJOR_SEV_CODE,
    MINOR: MINOR_SEV_CODE,
    WARNING: WARNING_SEV_CODE,
    INDETERMINATE: INDETER_SEV_CODE,
    CLEARED: CLEARED_SEV_CODE,
    NORMAL: NORMAL_SEV_CODE,
    OK: OK_SEV_CODE,
    INFORM: INFORM_SEV_CODE,
    DEBUG: DEBUG_SEV_CODE,
    AUTH: AUTH_SEV_CODE,
    UNKNOWN: UNKNOWN_SEV_CODE,
}

_DISPLAY_SEVERITY = {
    CRITICAL:      "Crit",
    MAJOR:         "Majr",
    MINOR:         "Minr",
    WARNING:       "Warn",
    INDETERMINATE: "Ind ",
    CLEARED:       "Clr",
    NORMAL:        "Norm",
    INFORM:        "Info",
    OK:            "Ok",
    DEBUG:         "Dbug",
    AUTH:          "Sec",
    UNKNOWN:       "Unkn"
}


class UpdateThread(threading.Thread):

    def __init__(self, endpoint, key):

        self.api = ApiClient(endpoint=endpoint, key=key)

        self.version = ''

        self.last_metrics = dict()
        self.app_last_time = None
        self.rate_metrics = dict()
        self.latency_metrics = dict()

        self.alerts = []
        self.total = 0
        self.status = ''
        self.groupby = None
        self.top10 = []

        self.last_time = datetime.utcnow()

        # self.prev_time = None
        # self.diff_time = 0
        # self.running_total = 0
        # self.start_time = time.time()
        # self.max_rate = 0.0
        # self.latency = 0
        # self.running_latency = 0
        #
        # self.dupl_cache = dict()
        # self.dupl_total = 0
        # self.running_dupl_total = 0

        self.running = True

        threading.Thread.__init__(self)

    def run(self):

        self.running = True

        while self.running:
            self.status = 'updating...'
            self._update()
            try:
                time.sleep(2)
            except (KeyboardInterrupt, SystemExit):
                sys.exit(0)

    def set_groupby(self, groupby):
        self.groupby = groupby

    def get_groupby(self):
        return self.groupby

    def _update(self):

        try:
            status = self.api.get_status()
        except ConnectionError:
            return ''

        self.version = 'v' + status['version']

        app_time = status['time'] / 1000  # epoch ms

        metrics = [metric for metric in status['metrics'] if metric['type'] == 'timer']
        for m in metrics:
            count = m['count']
            totalTime = m['totalTime']

            if m['name'] in self.last_metrics:
                (last_count, last_totalTime) = self.last_metrics[m['name']]
            else:
                self.last_metrics[m['name']] = (count, totalTime)
                self.app_last_time = app_time
                continue

            if count >= last_count:
                num = count - last_count
                period = app_time - self.app_last_time
                try:
                    rate = 1.0 * num / period
                except ZeroDivisionError:
                    rate = 0.0

                self.rate_metrics[m['name']] = rate

            if totalTime >= last_totalTime:
                diff = totalTime - last_totalTime
                num = count - last_count
                try:
                    latency = 1.0 * diff / num
                except ZeroDivisionError:
                    latency = 0.0

                self.latency_metrics[m['name']] = latency

            self.last_metrics[m['name']] = (count, totalTime)

        self.app_last_time = app_time

        try:
            response = self.api.get_alerts()
        except ConnectionError:
            return ''

        with lock:
            self.alerts = response.get('alerts', [])
            self.total = response.get('total', 0)
            self.status = '%s - %s' % (response['status'], response.get('message', 'no errors'))

        try:
            response = self.api.get_top10(self.groupby)
        except ConnectionError:
            return ''

        with lock:
            self.top10 = response.get('top10', [])


class Screen(object):

    ALIGN_RIGHT = 'R'
    ALIGN_CENTRE = 'C'

    def __init__(self, endpoint, key):

        self.endpoint = endpoint
        self.key = key

        self.screen = self._get_screen()
        self.min_y = 0
        self.min_x = 0
        self.max_y = 0
        self.max_x = 0
        self.cursor_pos = -1

        self.total_alerts = 0
        self.total_latency = 0
        self.start_time = time.time()
        self.max_rate = 0.0
        self.max_latency = 0
        self.last_time = None
        self.max_dupl_rate = 0.0

        self.w =None

    def run(self):

        self.w = UpdateThread(endpoint=self.endpoint, key=self.key)
        self.w.start()

        self.register_exit_handlers()
        self.mainloop()

    def mainloop(self):

        while True:
            try:
                self._redraw()
                event = self.screen.getch()

                if 0 < event < 256:
                    self._handle_key_event(chr(event))
                # elif event in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_PPAGE, curses.KEY_NPAGE]:
                #     self._handle_movement_key(event)
                else:
                    self._handle_event(event)

                time.sleep(SCREEN_REDRAW_INTERVAL)
            except Exception as e:
                print(e)
                self.w.running = False
                break

        self.w.join()

    def _get_screen(self):

        screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()

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

        self._COLOR_MAP = {
            "critical": COLOR_RED,
            "major": COLOR_MAGENTA,
            "minor": COLOR_YELLOW,
            "warning": COLOR_BLUE,
            "indeterminate": COLOR_CYAN,
            "cleared": COLOR_GREEN,
            "normal": COLOR_GREEN,
            "informational": COLOR_GREEN,
            "ok": COLOR_GREEN,
            "debug": COLOR_BLACK,
            "auth": COLOR_BLACK,
            "unknown": COLOR_BLACK
        }

        try:
            curses.curs_set(0)
        except Exception:
            pass

        screen.keypad(1)
        screen.nodelay(1)

        curses.def_prog_mode()

        return screen

    def _draw_header(self):

        now = datetime.utcnow().strftime("%H:%M:%S %d/%m/%y")

        self._addstr(self.min_y, self.min_x, self.endpoint, curses.A_BOLD)
        self._addstr(self.min_y, self.ALIGN_CENTRE, 'alerta ' + self.w.version, curses.A_BOLD)
        self._addstr(self.min_y, self.ALIGN_RIGHT, now, curses.A_BOLD)

    def _draw_bars(self):

        max_bars = self.max_x - 10 - 30

        if 'received' in self.w.rate_metrics:
            cur_rate = self.w.rate_metrics['received']
            if cur_rate > self.max_rate:
                self.max_rate = cur_rate
            try:
                bars = int(max_bars * cur_rate / self.max_rate)
            except ZeroDivisionError:
                bars = 0
        else:
            cur_rate = 0
            bars = 0

        self._addstr(self.min_y + 2, 1, "Rate     [%s%s] %2.1f/s %2.1f/s %2.1f/s" % (
            '#' * bars, ' ' * (max_bars - bars), cur_rate, 0, self.max_rate))

        if 'received' in self.w.latency_metrics:
            cur_latency = self.w.latency_metrics['received']
            if cur_latency > self.max_latency:
                self.max_latency = cur_latency
            try:
                bars = int(max_bars * cur_latency / self.max_latency)
            except ZeroDivisionError:
                bars = 0
        else:
            cur_latency = 0
            bars = 0

        self._addstr(self.min_y + 3, 1, "Latency  [%s%s] %3.fms %3.fms %3.fms" % (
            '#' * bars, ' ' * (max_bars - bars), cur_latency, 0, self.max_latency))

    def _draw_footer(self):

        self._addstr(self.max_y - 1, 0, "Last Update: %s (group by %s)" % (self.w.last_time.strftime("%H:%M:%S"), self.w.get_groupby()), curses.A_BOLD)
        self._addstr(self.max_y - 1, self.ALIGN_CENTRE, self.w.status, curses.A_BOLD)
        self._addstr(self.max_y - 1, self.ALIGN_RIGHT, "Count: %s" % self.w.total, curses.A_BOLD)

    def _addstr(self, y, x, str, attr=0):

        if x == self.ALIGN_RIGHT:
            x = self.max_x - len(str) - 1
        if x == self.ALIGN_CENTRE:
            x = int((self.max_x / 2) - len(str) / 2)

        self.screen.addstr(y, x, str, attr)

    def _draw_alerts(self):

        with lock:
            if self.w.get_groupby():
                self._addstr(2, 1, '{:<20} Count Dupl. Environments             Services                 Resources'.format(
                    self.w.get_groupby().capitalize()
                ), curses.A_UNDERLINE)
                i = 2
                alerts = copy.deepcopy(self.w.top10)
                for alert in alerts:
                    i += 1
                    try:
                        self._addstr(i, 1, '{:<20} {:5} {:5} {:<24} {:<24} {}'.format(
                            alert[self.w.get_groupby()],
                            alert['count'],
                            alert['duplicateCount'],
                            ','.join(alert['environments']),
                            ','.join(alert['services']),
                            ','.join([r['resource'] for r in alert['resources']]),
                            self.max_x - 160
                        ))
                    except curses.error as e:
                        print(e)
                        sys.exit(1)
                    except Exception:
                        break
                    if i == self.max_y - 3:
                        break
            else:
                if self.max_x < 132:
                    self._addstr(2, 1, 'Sev. Time     Dupl. Env.         Service      Resource     Event        Value ',
                                 curses.A_UNDERLINE)
                else:
                    self._addstr(2, 1, 'Sev. Last Recv. Time Dupl. Customer Environment  Service      Resource ' +
                                       '      Event          Value   Text' + ' ' * (self.max_x - 106), curses.A_UNDERLINE)

                def name_to_code(name):
                    return _SEVERITY_MAP.get(name.lower(), UNKNOWN_SEV_CODE)

                def to_short_sev(severity):
                    return _DISPLAY_SEVERITY.get(severity, _DISPLAY_SEVERITY['unknown'])

                i = 2
                #self._addstr(1,1, '%sx%s' % (self.max_y, self.max_x))
                alerts = copy.deepcopy(self.w.alerts)
                for alert in sorted(alerts, key=lambda x: name_to_code(x['severity'])):
                    a = AlertDocument.parse_alert(alert)
                    i += 1
                    color = self._COLOR_MAP.get(a.severity, self._COLOR_MAP['unknown'])
                    try:
                        if self.max_x < 132:
                            self._addstr(i, 1, '{0:<4} {1} {2:5d} {3:<12} {4:<12} {5:<12.12} {6:<12.12} {7:<6.6}'.format(
                                to_short_sev(a.severity),
                                a.get_date('last_receive_time', 'short')[7:],
                                a.duplicate_count,
                                a.environment,
                                ','.join(a.service),
                                a.resource,
                                a.event,
                                a.value
                            ), color)
                        else:
                            self._addstr(i, 1, '{0:<4} {1} {2:5d} {3:>8.8} {4:<12} {5:<12} {6:<14.14} {7:<14.14} {8:<7.7} {9:{10}.{10}}'.format(
                                to_short_sev(a.severity),
                                a.get_date('last_receive_time', 'short'),
                                a.duplicate_count,
                                a.customer or '-',
                                a.environment,
                                ','.join(a.service),
                                a.resource,
                                a.event,
                                a.value,
                                a.text,
                                self.max_x - 106
                            ), color)
                    except curses.error as e:
                        print(e)
                        sys.exit(1)
                    if i == self.max_y - 3:
                        break

    def _update_max_size(self):

        max_y, max_x = self.screen.getmaxyx()

        self.max_y = max_y
        self.max_x = max_x

    def _redraw(self):

        self._update_max_size()
        self.screen.clear()

        self._draw_header()
        # if not self.w.get_groupby():
        #     self._draw_bars()
        self._draw_alerts()
        self._draw_footer()

        curses.doupdate()

    def _reset(self):

        self.screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    # Event handlers
    def _handle_key_event(self, key):
        if key in 'aA':
            self.w.set_groupby(groupby=None)
        elif key in 'eE':
            self.w.set_groupby("event")
        elif key in 'rR':
            self.w.set_groupby("resource")
        elif key in 'gG':
            self.w.set_groupby("group")
        elif key in 'oO':
            self.w.set_groupby("origin")
        elif key in 'tT':
            self.w.set_groupby("type")
        elif key in 'cC':
            self.w.set_groupby("customer")
        elif key in 'sS':
            self.w.set_groupby("severity")
        elif key in 'vV':
            self.w.set_groupby("value")
        elif key in 'qQ':
            self._reset()
            sys.exit(0)

    # def _handle_movement_key(self, key):
    #     # Highlight the corresponding node in the list
    #     self.max_cursor_pos = len(self.table_lines) - 1
    #     if key == curses.KEY_UP:
    #         if self.cursor_pos > self.min_cursor_pos:
    #             self.cursor_pos -= 1
    #
    #     elif key == curses.KEY_DOWN:
    #         if self.cursor_pos < self.max_cursor_pos:
    #             self.cursor_pos += 1
    #
    #     elif key == curses.KEY_PPAGE:
    #         self.cursor_pos = 0
    #
    #     elif key == curses.KEY_NPAGE:
    #         self.cursor_pos = self.max_cursor_pos
    #
    #     self._update_node_metrics(update_now=True)

    def _handle_event(self, event):
        if event == curses.KEY_RESIZE:
            # Redraw the screen on resize
            self._redraw()

    def exit_handler(signum, frame):

        curses.echo()
        curses.nocbreak()
        curses.endwin()
        sys.exit(0)

    def register_exit_handlers(self):
        # Register exit signals
        signal.signal(signal.SIGTERM, self.exit_handler)
        signal.signal(signal.SIGINT, self.exit_handler)
