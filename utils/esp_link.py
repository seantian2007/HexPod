"""Talk to the stage 7/8 ESP32 firmware over WiFi (UDP) or USB serial, the same way.

    link = open_link(args)          # UdpLink by default, SerialLink with --serial PORT
    link.on_line = print            # called for every log line (text, no prefix)
    link.send('C,1,0,0.5,0')        # one protocol line
    link.event('A')                 # button event: numbered, sent 3 times over UDP
    link.start_recording()          # per-frame data -> logs/<date>_<time>.csv (UDP only)
    link.close()

What arrives from the ESP32 over UDP (see the top of hexapod.ino):
    L,<text>   log / statistics line   -> on_line(text)
    H,<names>  CSV column names        -> header of the log file
    D,<values> one control frame       -> one CSV row
    P,<n>      ping answer             -> ping() returns the round-trip time
Over serial there is no prefix: every line is a log line, and there is no D data
(50 Hz x ~200 bytes would not fit through 115200 baud next to the log).
"""
import os
import queue
import socket
import threading
import time

ROBOT_IP = '192.168.4.1'
ROBOT_PORT = 1234
SERIAL_PORT = '/dev/cu.usbserial-0001'
EVENT_COPIES = 3          # each button event is sent this many times over UDP...
EVENT_GAP = 0.02          # ...this far apart (s); the ESP32 executes one copy per id


def add_link_args(ap):
    """Command-line options shared by every script that talks to the robot."""
    ap.add_argument('--serial', nargs='?', const=SERIAL_PORT, default=None, metavar='PORT',
                    help=f'use USB serial instead of WiFi (default port {SERIAL_PORT})')
    ap.add_argument('--host', default=ROBOT_IP, help='robot IP over WiFi')


def open_link(args):
    if args.serial:
        return SerialLink(args.serial)
    return UdpLink(args.host)


class _Link:
    """Shared part: event numbering, the log queue, the CSV recorder."""

    def __init__(self):
        self.on_line = lambda text: print(f'[esp32] {text}')
        self.lines = queue.Queue()            # every log line, for wait_for()
        # Event ids start from the clock in ms, so a restarted script always starts above
        # the last id the ESP32 remembers (it ignores any id not newer than the last one,
        # which also drops a late copy of an earlier event). 32 bits, like the ESP32.
        self._event_id = int(time.time() * 1000) & 0xFFFFFFFF
        self._csv = None
        self._csv_lock = threading.Lock()

    # -- sending --
    def send(self, line):
        raise NotImplementedError

    def event(self, x):
        """Button event x in 'ABNPZ'. Numbered so the ESP32 runs it once even if copies arrive."""
        self._event_id = (self._event_id + 1) & 0xFFFFFFFF
        line = f'E,{self._event_id},{x}'
        self.send(line)
        for k in range(1, self._copies()):
            threading.Timer(k * EVENT_GAP, self.send, args=(line,)).start()

    def _copies(self):
        return 1

    # -- receiving --
    def _got_log(self, text):
        self.lines.put(text)
        self.on_line(text)

    def wait_for(self, prefix, timeout):
        """Block until a log line starting with prefix arrives; return it."""
        end = time.time() + timeout
        while time.time() < end:
            try:
                line = self.lines.get(timeout=0.1)
            except queue.Empty:
                continue
            if line.startswith(prefix):
                return line
        raise TimeoutError(f'no "{prefix}" from the robot within {timeout} s')

    # -- data log --
    def start_recording(self, folder='logs'):
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, time.strftime('%Y%m%d_%H%M%S') + '.csv')
        with self._csv_lock:
            self._csv = open(path, 'w')
        self.send('R,1')
        return path

    def stop_recording(self):
        self.send('R,0')
        time.sleep(0.1)                       # let the last frames arrive
        with self._csv_lock:
            if self._csv:
                self._csv.close()
                self._csv = None

    @property
    def recording(self):
        return self._csv is not None

    def _got_data(self, kind, text):
        with self._csv_lock:
            if self._csv:
                self._csv.write(text + '\n')  # H = column names, D = one frame: both are CSV lines

    def close(self):
        if self.recording:
            self.stop_recording()


class UdpLink(_Link):
    def __init__(self, host=ROBOT_IP, port=ROBOT_PORT):
        super().__init__()
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))               # any free port; the ESP32 answers to it
        self.sock.settimeout(0.2)
        self._pings = queue.Queue()
        self._stop = threading.Event()
        threading.Thread(target=self._reader, daemon=True).start()

    def _copies(self):
        return EVENT_COPIES

    def send(self, line):
        try:
            self.sock.sendto(line.encode(), self.addr)
        except OSError as e:                  # e.g. laptop not on the robot's WiFi
            raise SystemExit(f'cannot reach the robot at {self.addr[0]}: {e}. '
                             'Is this computer connected to the hexapod-xxxx WiFi?')

    def _reader(self):
        while not self._stop.is_set():
            try:
                data, _ = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError:
                return
            text = data.decode(errors='replace').strip()
            kind, _, rest = text.partition(',')
            if kind == 'L':
                self._got_log(rest)
            elif kind in ('H', 'D'):
                self._got_data(kind, rest)
            elif kind == 'P':
                self._pings.put((rest, time.perf_counter()))

    def ping(self, n, timeout=0.5):
        """Send ping n; return the round-trip time in ms, or None if no answer in time."""
        t0 = time.perf_counter()
        self.send(f'P,{n}')
        end = t0 + timeout
        while True:
            left = end - time.perf_counter()
            if left <= 0:
                return None
            try:
                got, t1 = self._pings.get(timeout=left)
            except queue.Empty:
                return None
            if got == str(n):
                return (t1 - t0) * 1000
            # an old, late answer: ignore it and keep waiting

    def close(self):
        super().close()
        self._stop.set()
        self.sock.close()


class SerialLink(_Link):
    def __init__(self, port=SERIAL_PORT):
        import serial                         # only needed for USB
        super().__init__()
        self._serial = serial
        self.ser = serial.Serial()
        self.ser.port, self.ser.baudrate, self.ser.timeout = port, 115200, 0.2
        self.ser.dtr = self.ser.rts = False   # (on the Mac, opening the port still resets the ESP32)
        self.ser.open()
        self._stop = threading.Event()
        threading.Thread(target=self._reader, daemon=True).start()

    def send(self, line):
        try:
            self.ser.write((line + '\n').encode())
        except self._serial.SerialException:
            raise SystemExit('USB disconnected: the robot stops by itself after 300 ms')

    def _reader(self):
        while not self._stop.is_set():
            try:
                line = self.ser.readline().decode(errors='replace').strip()
            except self._serial.SerialException:
                return
            if line:
                self._got_log(line)

    def start_recording(self, folder='logs'):
        print('recording needs WiFi: over USB the ESP32 does not send per-frame data')
        return None

    def close(self):
        super().close()
        self._stop.set()
        self.ser.close()
