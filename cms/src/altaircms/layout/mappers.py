# coding: utf-8
from bpmappers import Mapper
from bpmappers.fields import RawField, DelegateField, ListDelegateField


class LayoutMapper(Mapper):
    def after_filter_id(self, value):
        return int(value)

    id = RawField()
    title = RawField()
    blocks = RawField()
    template_filename = RawField()


class LayoutsMapper(Mapper):
    layouts = ListDelegateField(LayoutMapper)
