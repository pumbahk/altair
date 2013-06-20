# -*- coding:utf-8 -*-

from wtforms.fields.core import Field, UnboundField
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm.interfaces import MapperProperty
from sqlalchemy.schema import Column
from altair.viewhelpers.datetime_ import DefaultDateTimeFormatter, DateTimeHelper

date_time_formatter = DefaultDateTimeFormatter()
date_time_helper = DateTimeHelper(date_time_formatter)

__all__ = [
    'jdate',
    'jtime',
    'jdatetime',
    'label_text_for',
    'column_name_for',
    ]

jdate = date_time_helper.date
jtime = date_time_helper.time
jdatetime = date_time_helper.datetime

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
