#-*- coding: utf-8 -*-
"""多重起動防止用のユーティリティ
"""
import sqlahelper


class AlreadyStartUpError(Exception):
    """既に起動している場合のエラー
    """
    pass


class MultiStartLock(object):
    """多重起動防止用

    Lockが既に取得されている場合はAlreadyStartUpError例外が送出されます。

    >>> with MultiStartLock('lock_name', 10):
    >>>     pass # statements
    >>>

    もし例外を細くしたい場合は次のようにしてください。

    >>> try:
    >>>     with MultiStartLock():
    >>>         pass # statements
    >>> except AlreadyStartUpError as err:
    >>>     pass # statements
    """
    def __init__(self, name, timeout=10):
        self.name = name
        self.timeout = int(timeout)

    def __enter__(self):
        rc = self._get_lock()
        if rc != 1:
            raise AlreadyStartUpError(
                'Lock timeout: name={}: already running process'.format(
                    self.name))

    def _get_lock(self):
        self._conn = sqlahelper.get_engine().connect()
        return self._conn.scalar('select get_lock(%s,%s)',
                                 (self.name, self.timeout))

    def __exit__(self, exc_type, exc_value, traceback):
        self._conn.close()
