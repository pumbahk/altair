#-*- coding: utf-8 -*-
"""多重起動防止用のユーティリティ
"""

from .errors import AlreadyStartUpError
from .lock import MultiStartLock

__all__ = ['AlreadyStartUpError', 'MultiStartLock']

__version__ = '1.0.0'
