#-*- coding: utf-8 -*-
class AlreadyStartUpError(Exception):
    pass

import sqlahelper
class MultiStartLock(object):
    def __init__(self, name, timeout=10):
        self.name = name
        self.timeout = int(timeout)

    def __enter__(self):
        rc = self._get_lock()
        if rc != 1:
            raise AlreadyStartUpError()

    def _get_lock(self):
        self._conn = sqlahelper.get_engine().connect()
        return self._conn.scalar('select get_lock(%s,%s)',
                                 (self.name, self.timeout))

    def __exit__(self, exc_type, exc_value, traceback):
        self._conn.close()
