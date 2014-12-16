import signal

class TimeoutError(Exception):
    pass

class Watchdog(object):
    def __init__(self, secs):
        self.timeout = secs
        self.prev_handler = None

    def __enter__(self):
        if self.timeout is not None:
            self.prev_handler = signal.signal(signal.SIGALRM, self._timeout)
            signal.alarm(self.timeout)
        return self

    def __exit__(self, type_, value, traceback):
        if self.prev_handler is not None:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, self.prev_handler)

    def _timeout(self, sig, frame):
        raise TimeoutError('execution has not been completed in %d seconds.' % self.timeout)

