#-*- coding: utf-8 -*-
"""多重起動防止用のユーティリティ
"""
from .errors import AlreadyStartUpError

GRASP = True
NOT_GRASP = False

class MultiStartLock(object):
    """多重起動防止用

    Lockが既に取得されている場合はAlreadyStartUpError例外が送出されます。

    >>> with MultiStartLock('lock_name', 10):
    >>>     pass # statements
    >>>

    もし例外を補足したい場合は次のようにしてください。

    >>> try:
    >>>     with MultiStartLock('lock_name'):
    >>>         pass # statements
    >>> except AlreadyStartUpError as err:
    >>>     pass # statements
    """
    def __init__(self, name, timeout=10, engine=None):
        self.name = name
        self.timeout = int(timeout)
        if engine is None:
            import sqlahelper
            engine = sqlahelper.get_engine()
        self.engine = engine

    def __enter__(self):
        rc = self.get_lock()
        if rc != GRASP:
            raise AlreadyStartUpError(
                'Lock timeout: name={}: already running process'.format(
                    self.name))

    def __exit__(self, exc_type, exc_value, traceback):
        self.release_lock()

    def get_lock(self):
        self._conn = self.engine.connect()
        rc = self._conn.scalar('select get_lock(%s,%s)',
                               (self.name, self.timeout))
        return GRASP if rc == 1 else NOT_GRASP

    def release_lock(self):
        self._conn.close()
