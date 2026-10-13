import math
import statistics
import threading
import time


class Accumulator:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        with self.lock:
            self.pressed = {}
            self.previous_press = None
            self.position = None
            self.dwell, self.intervals, self.speeds = [], [], []
            self.scroll_interval = None
            self.scroll_burst = None
            self.scroll_intervals = []
            self.scroll_bursts = []
            self.overflow = False

    def append(self, values, value):
        if len(values) < 512:
            values.append(value)
        else:
            self.overflow = True

    def press(self, key, now):
        with self.lock:
            if key in self.pressed:
                return
            if len(self.pressed) >= 64:
                self.overflow = True
                return
            self.pressed[key] = now
            if self.previous_press is not None and 0 < now - self.previous_press < 2:
                self.append(self.intervals, now - self.previous_press)
            self.previous_press = now

    def release(self, key, now):
        with self.lock:
            start = self.pressed.pop(key, None)
            if start is not None and 0 < now - start < 2:
                self.append(self.dwell, now - start)

    def move(self, x, y, now):
        with self.lock:
            if self.position:
                px, py, previous = self.position
                interval = now - previous
                if interval < 0.02:
                    return
                if interval < 1:
                    self.append(self.speeds, math.hypot(x - px, y - py) / interval)
            self.position = (x, y, now)

    def scroll(self, dy, now):
        with self.lock:
            if self.scroll_interval is not None and 0 < now - self.scroll_interval < 2:
                self.append(self.scroll_intervals, now - self.scroll_interval)
            if self.scroll_burst is not None and 0 < now - self.scroll_burst < 2:
                self.append(self.scroll_bursts, now - self.scroll_burst)
            self.scroll_interval = now
            if self.scroll_burst is None or now - self.scroll_burst > 0.5:
                self.scroll_burst = now

    def window(self):
        with self.lock:
            result = {}
            if not self.overflow:
                for name, values, minimum in (
                    ("key_dwell", self.dwell, 5),
                    ("key_interval", self.intervals, 5),
                    ("pointer_speed", self.speeds, 10),
                    ("scroll_interval", self.scroll_intervals, 3),
                    ("scroll_burst", self.scroll_bursts, 3),
                ):
                    if len(values) >= minimum:
                        result[name] = statistics.median(values)
            self.dwell, self.intervals, self.speeds = [], [], []
            self.scroll_intervals, self.scroll_bursts = [], []
            self.pressed.clear()
            self.previous_press = None
            self.position = None
            self.scroll_interval = None
            self.scroll_burst = None
            self.scroll_intervals = []
            self.scroll_bursts = []
            self.overflow = False
            return result


class Capture:
    def __init__(self):
        self.accumulator = Accumulator()
        self.listeners = []

    def start(self, consent):
        if not consent:
            raise PermissionError("Consent is required before capture.")
        self.stop()
        from pynput import keyboard, mouse

        self.listeners = [
            keyboard.Listener(
                on_press=lambda key: self.accumulator.press(key, time.monotonic()),
                on_release=lambda key: self.accumulator.release(key, time.monotonic()),
            ),
            mouse.Listener(
                on_move=lambda x, y: self.accumulator.move(x, y, time.monotonic()),
                on_scroll=lambda x, y, dx, dy: self.accumulator.scroll(dy, time.monotonic()),
            ),
        ]
        try:
            for listener in self.listeners:
                listener.start()
                listener.wait()
        except Exception:
            self.stop()
            raise

    def stop(self):
        for listener in self.listeners:
            listener.stop()
        for listener in self.listeners:
            listener.join(timeout=2)
            if listener.is_alive():
                raise RuntimeError(
                    "Input listener did not stop; do not enter a password."
                )
        self.listeners = []
        self.accumulator.reset()

    def window(self):
        if not self.listeners or not all(
            listener.is_alive() for listener in self.listeners
        ):
            raise RuntimeError("Input monitoring stopped unexpectedly.")
        return self.accumulator.window()
