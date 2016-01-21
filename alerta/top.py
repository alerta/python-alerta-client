
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

    def __init__(self, endpoint, key, interval=2):

        self.api = ApiClient(endpoint=endpoint, key=key)

        self.interval = interval

        self.version = ''

        self.last_metrics = dict()
        self.app_last_time = None
        self.rate_metrics = dict()
        self.latency_metrics = dict()

        self.status = ''
        self.total = 0
        self.alerts = []
        self.last_time = datetime.utcnow()

        self.resources = dict()
        self.events = dict()
        self.origins = dict()

        self.prev_time = None
        self.diff_time = 0
        self.running_total = 0
        self.start_time = time.time()
        self.max_rate = 0.0
        self.latency = 0
        self.running_latency = 0

        self.dupl_cache = dict()
        self.dupl_total = 0
        self.running_dupl_total = 0

        self.running = True

        threading.Thread.__init__(self)

    def run(self):

        self.running = True

        now = datetime.utcnow()
        from_date = now.replace(microsecond=0).isoformat() + ".%03dZ" % (now.microsecond // 1000)

        while self.running:
            self.status = 'updating...'
            from_date = self._update(from_date)
            try:
                time.sleep(self.interval)
            except (KeyboardInterrupt, SystemExit):
                sys.exit(0)

    def _update(self, from_date=None):

        status = self.api.get_status()

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

        query = {'from-date': from_date}
        response = self.api.get_alerts(query)

        with lock:
            self.status = '%s - %s' % (response['status'], response.get('message', 'no errors'))
            self.total = response.get('total', 0)
            alert_delta = response.get('alerts', [])
            self.last_time = datetime.strptime(response.get('lastTime', ''), "%Y-%m-%dT%H:%M:%S.%fZ")

            for alert in alert_delta:

                key = (alert['environment'], alert['resource'])
                if key not in self.resources:
                    self.resources[key] = dict()
                    self.resources[key]['count'] = 0
                self.resources[key]['count'] += 1
                self.resources[key]['environment'] = alert['environment']
                self.resources[key]['resource'] = alert['resource']

                key = alert['event']
                if key not in self.events:
                    self.events[key] = dict()
                    self.events[key]['count'] = 0
                self.events[key]['count'] += 1
                self.events[key]['group'] = alert['group']
                self.events[key]['event'] = alert['event']

                key = alert['origin']
                if key not in self.origins:
                    self.origins[key] = dict()
                    self.origins[key]['count'] = 0
                self.origins[key]['count'] += 1
                self.origins[key]['origin'] = alert['origin']

        response = self.api.get_alerts({})
        with lock:
            self.alerts = response.get('alerts', [])
            self.total = response.get('total', 0)

        return response.get('lastTime', '')


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

        self.dedup_by = None

    def run(self):

        self.w = UpdateThread(endpoint=self.endpoint, key=self.key)
        self.w.start()

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

        self._addstr(self.max_y - 1, 0, "Last Update: %s" % self.w.last_time.strftime("%H:%M:%S"), curses.A_BOLD)
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
            if self.dedup_by == "resource" and self.w.resources:

                self._addstr(5, 1, 'Count Environment Resource', curses.A_BOLD)

                i = 5  # start after line 5
                for key in sorted(self.w.resources, key=lambda x: self.w.resources[x]['count'], reverse=True):
                    i += 1
                    try:
                        self._addstr(i, 1, '%5s %-11s %-30s' % (
                            self.w.resources[key]['count'],
                            self.w.resources[key]['environment'],
                            self.w.resources[key]['resource'])
                        )
                    except curses.error:
                        pass
                    if i == self.max_y - 3:
                        break

            elif self.dedup_by == "event" and self.w.events:

                self._addstr(5, 1, 'Count Group       Event', curses.A_BOLD)

                i = 5  # start after line 5
                for key in sorted(self.w.events, key=lambda x: self.w.events[x]['count'], reverse=True):
                    i += 1
                    try:
                        self._addstr(i, 1, '%5s %-11s %-30s' % (
                            self.w.events[key]['count'],
                            self.w.events[key]['group'],
                            self.w.events[key]['event'])
                        )
                    except curses.error:
                        pass
                    if i == self.max_y - 3:
                        break

            elif self.dedup_by == "origin" and self.w.origins:

                self._addstr(5, 1, 'Count Origin', curses.A_BOLD)

                i = 5  # start after line 5
                for key in sorted(self.w.origins, key=lambda x: self.w.origins[x]['count'], reverse=True):
                    i += 1
                    try:
                        self._addstr(i, 1, '%5s %-30s' % (
                            self.w.origins[key]['count'],
                            self.w.origins[key]['origin']
                        ))
                    except curses.error:
                        pass
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
        if self.dedup_by:
            self._draw_bars()
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
            self.dedup_by = None
        elif key in 'rR':
            self.dedup_by = "resource"
        elif key in 'eE':
            self.dedup_by = "event"
        elif key in 'oO':
            self.dedup_by = "origin"
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

# Register exit signals
signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)
