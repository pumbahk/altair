from datetime import datetime
import sqlahelper
from sqlalchemy import (
    Column,
)
from sqlalchemy.types import (
    Integer,
    BigInteger,
    TIMESTAMP,
)
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import (
    deferred,
)
from sqlalchemy.ext.declarative import declared_attr


class Identifier(Integer):
    def __init__(self, *args, **kwargs):
        self._inner = None
        self._args = args
        self._kwargs = kwargs

    def _compiler_dispatch(self, visitor, **kw):
        return self.inner._compiler_dispatch(visitor, **kw)

    @property
    def inner(self):
        if self._inner is None:
            type_ = BigInteger
            try:
                if sqlahelper.get_engine().dialect.name == 'sqlite':
                    type_ = Integer
            except:
                pass
            self._inner = type_(*self._args, **self._kwargs)
        return self._inner

    def get_dbapi_type(self, dbapi):
        return self.inner.get_dbapi_type(dbapi)

    @property
    def python_type(self):
        return self.inner.python_type

    @property
    def _expression_adaptations(self):
        return self.inner._expression_adaptations

class WithTimestamp(object):
    __clone_excluded__ = ['created_at', 'updated_at']

    @declared_attr
    def created_at(self):
        return deferred(Column(TIMESTAMP, nullable=False,
                               default=datetime.now,
                               server_default=sqlf.current_timestamp()))
    @declared_attr
    def updated_at(self):
        return deferred(Column(TIMESTAMP, nullable=False,
                               default=datetime.now,
                               server_default=text('0'),
                               onupdate=datetime.now,
                               server_onupdate=sqlf.current_timestamp()))

class LogicallyDeleted(object):
    __clone_excluded__ = ['deleted_at']

    @declared_attr
    def deleted_at(self):
        return deferred(Column(TIMESTAMP, nullable=True, index=True))

