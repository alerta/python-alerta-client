
import sys
import time
import urllib
import requests
import curses
import threading
import signal

from datetime import datetime

SCREEN_REDRAW_INTERVAL = 2
lock = threading.Lock()


class Alert(threading.Thread):

    def __init__(self, endpoint="http://localhost:8080", filter=None, interval=2):

        self.endpoint = endpoint
        self.filter = filter or list()
        self.interval = interval
        self.from_date = datetime.utcnow().isoformat()+'Z'

        self.last_metrics = dict()
        self.app_last_time = None
        self.rate_metrics = dict()
        self.latency_metrics = dict()

        self.status = ''
        self.total = 0
        self.alerts = None
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

        while self.running:
            self.status = 'updating...'
            self.from_date = self._get_alerts(self.filter, self.from_date)
            try:
                time.sleep(self.interval)
            except (KeyboardInterrupt, SystemExit):
                sys.exit(0)

    def _get_alerts(self, filter, from_date=None):

        url = self.endpoint + '/management/status'
        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError, e:
            pass

        status = response.json()

        app_time = status['time'] / 1000  # epoch ms

        metrics = [metric for metric in status['metrics'] if metric['type'] == u'timer']
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

        query = dict([x.split('=', 1) for x in filter if '=' in x])

        if from_date:
            query['from-date'] = from_date

        if 'sort-by' not in query:
            query['sort-by'] = 'lastReceiveTime'

        url = self.endpoint + '/api/alerts?' + urllib.urlencode(query, doseq=True)
        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError, e:
            pass

        response = response.json()

        with lock:
            self.status = '%s - %s' % (response['status'], response.get('message', 'no errors'))
            self.total = response.get('total', 0)
            self.alerts = response.get('alerts', [])
            self.last_time = datetime.strptime(response.get('lastTime', ''), "%Y-%m-%dT%H:%M:%S.%fZ")

            for alert in self.alerts:

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

        return response.get('lastTime', '')


class Screen(object):

    ALIGN_RIGHT = 'R'
    ALIGN_CENTRE = 'C'

    def __init__(self, args):

        self.endpoint = args.endpoint

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

        self.dedup_by = "resource"

    def run(self):

        self.w = Alert(endpoint=self.endpoint)
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
            except Exception:
                self.w.running = False
                break

        self.w.join()

    def _get_screen(self):

        screen = curses.initscr()
        curses.noecho()

        try:
            curses.curs_set(0)
        except Exception, e:
            pass

        screen.keypad(1)
        screen.nodelay(1)

        curses.def_prog_mode()

        return screen

    def _draw_header(self):

        now = datetime.utcnow().strftime("%H:%M:%S %d/%m/%y")

        self._addstr(self.min_y, self.min_x, self.w.endpoint, curses.A_BOLD)
        self._addstr(self.min_y, self.ALIGN_CENTRE, 'alerta', curses.A_BOLD)
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
                    except curses.error, e:
                        pass
                    if i == self.max_y - 3:
                        break

            if self.dedup_by == "event" and self.w.events:

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
                    except curses.error, e:
                        pass
                    if i == self.max_y - 3:
                        break

            if self.dedup_by == "origin" and self.w.origins:

                self._addstr(5, 1, 'Count Origin', curses.A_BOLD)

                i = 5  # start after line 5
                for key in sorted(self.w.origins, key=lambda x: self.w.origins[x]['count'], reverse=True):
                    i += 1
                    try:
                        self._addstr(i, 1, '%5s %-30s' % (
                            self.w.origins[key]['count'],
                            self.w.origins[key]['origin']
                        ))
                    except curses.error, e:
                        pass
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
        if key in 'rR':
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
