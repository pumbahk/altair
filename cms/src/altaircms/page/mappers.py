# coding: utf-8
from bpmappers.fields import ListDelegateField
from bpmappers.mappers import Mapper


class PageMapper(Mapper):
    pass


class PagesMapper(Mapper):
    pages = ListDelegateField(PageMapper)