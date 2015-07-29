from weakref import WeakKeyDictionary
from sqlalchemy.schema import Column as _Column
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.orm.interfaces import MANYTOMANY

from sqlalchemy.ext.associationproxy import AssociationProxy

__all__ = [
    'AnnotatedColumn',
    'get_annotations_for',
    ]

annotations_dict = WeakKeyDictionary()

class AnnotatedColumn(_Column):
    """
    You may well think it will suffice for this to be a callable, but
    it'd be safe to allow one to assert this through isinstance()...
    """
    def __new__(cls, *args, **kwargs):
        annotations = kwargs.pop('_annotations', None)
        for k in list(kwargs.keys()):
            if k.startswith('_a_'):
                if annotations is None:
                    annotations = {}
                annotations[k[3:]] = kwargs.pop(k)
        new_instance = _Column(*args, **kwargs)
        if annotations:
            annotations_dict[new_instance] = annotations
        return new_instance

def get_annotations_for(misc):
    if not isinstance(misc, (_Column, AssociationProxy, QueryableAttribute, ColumnProperty, RelationshipProperty)):
        raise Exception('unsupported type: %s' % misc.__class__.__name__)
    annotations = annotations_dict.get(misc)
    if annotations is None:
        if isinstance(misc, AssociationProxy):
            misc = misc.remote_attr
        if isinstance(misc, QueryableAttribute):
            misc = misc.property

        columns = None

        if isinstance(misc, ColumnProperty):
            columns = misc.columns
        elif isinstance(misc, RelationshipProperty):
            if misc.direction == MANYTOMANY:
                columns = [pair[0] for pair in misc.secondary_synchronize_pairs]
            else:
                columns = [pair[0] for pair in misc.local_remote_pairs]
        if columns is not None:
            annotations_list = []
            for column in columns:
                annotations = annotations_dict.get(column)
                if annotations is not None:
                    annotations_list.append(annotations)
            if len(annotations_list) == 1:
                # most likely
                annotations = annotations_list[0]
            elif len(annotations_list) > 1:
                raise Exception("more than one columns are associated to ColumnProperty '%r'" % misc)
        if annotations is not None:
            annotations_dict[misc] = annotations
    return annotations

