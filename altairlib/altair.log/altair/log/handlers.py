import logging
import logging.handlers

class SpoolingHandler(logging.handlers.MemoryHandler):
    def __init__(self, *args, **kwargs):
        super(SpoolingHandler, self).__init__(*args, **kwargs)
        self.flushed = False

    def shouldFlush(self, record):
        return super(SpoolingHandler, self).shouldFlush(record)

    def emit(self, record):
        self.buffer.append(record)
        if self.flushed or self.shouldFlush(record):
            self.flushed = True
            super(SpoolingHandler, self).flush()

    def flush(self):
        if self.flushed:
            super(SpoolingHandler, self).flush()

