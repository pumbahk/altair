# -*- coding:utf-8 -*-

from wtforms.fields.core import Field, UnboundField
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm.interfaces import MapperProperty
from sqlalchemy.schema import Column

__all__ = [
    'jdate',
    'jtime',
    'jdatetime',
    'label_text_for',
    'column_name_for',
    ]

WEEK = [u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
def jdate(d):
    """ dateオブジェクトを受け取り日本語の日付を返す
    >>> from datetime import date
    >>> jdate(date(2011, 1, 1))
    u'2011\u5e7401\u670801\u65e5'
    """
    if d:
        datestr = d.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8")
        return u"%s（%s）" % (datestr, unicode(WEEK[d.weekday()]))
    else:
        return u"-"

def jtime(d):
    """datetimeオブジェクトを受け取り日本語の時刻を返す
    """
    if d:
        return d.strftime(u"%H時%M分".encode("utf-8")).decode("utf-8")
    else:
        return u"-"

def jdatetime(d):
    """datetimeオブジェクトを受け取り日本語の日時を返す
    """
    if d:
        datestr = jdate(d)
        timestr = jtime(d)
        return u"%s%s" % (datestr, timestr)
    else:
        return u"-"

def label_text_for(misc):
    from altair.saannotation import get_annotations_for
    label = None
    if isinstance(misc, Field):
        label = misc.label.text
    elif isinstance(misc, UnboundField):
        label = misc.kwargs.get('label')
    else:
        annotations = get_annotations_for(misc)
        if annotations:
            label = annotations.get('label')
    if label is None:
        raise ValueError('no label for %r' % misc)
    return label

def column_name_for(misc):
    if isinstance(misc, Field):
        return misc.name
    elif isinstance(misc, UnboundField):
        return misc.kwargs.get('name')
    elif isinstance(misc, QueryableAttribute):
        return misc.property.key
    elif isinstance(misc, MapperProperty):
        return misc.key
    elif isinstance(misc, Column):
        return misc.name
    raise ValueError('no column name for %r' % misc)
