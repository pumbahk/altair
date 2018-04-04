# encoding: utf-8

from collections import Sequence
from math import ceil

from .exceptions import PageNotInInteger, EmptyPage
__all__ = ['Paginator']

class Page(Sequence):
    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self):
        return '<Page {0} of {1}>'.format(self.number, self.paginator.num_pages)

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        if not isinstance(index, (int, slice)):
            raise TypeError
        if not isinstance(self.object_list, list):
            self.object_list = list(self.object_list)
        return self.object_list[index]

    @property
    def has_next(self):
        return self.number < self.paginator.num_pages

    @property
    def has_previous(self):
        return self.number > 1

    @property
    def next_page_number(self):
        return self.paginator.validate_number(self.number + 1)

    @property
    def previous_page_number(self):
        return self.paginator.validate_number(self.number - 1)

    @property
    def start_index(self):
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    @property
    def end_index(self):
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page


class Paginator(object):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page = int(per_page)
        self.orphans = int(orphans)
        self.allow_empty_first_page = allow_empty_first_page

    def validate_number(self, number):
        try:
            number = int(number)
        except(TypeError, ValueError):
            raise PageNotInInteger('The page number should be integer but got {}'.format(number))
        if number < 1:
            raise EmptyPage('The page number should be greater or equal to 1 but got {}'.format(number))
        if number > self.num_pages:
            if not (number == 1 and self.allow_empty_first_page):
                raise EmptyPage('There is no result on this page: {}.'.format(number))
        return number

    def page(self, number):

        number = self.validate_number(number)
        start = (number - 1) * self.per_page
        end = start + self.per_page

        if end + self.orphans >= self.count:
            end = self.count
        return self._get_page(self.object_list[start:end], number, self)

    def _get_page(self, *args, **kwargs):
        return Page(*args, **kwargs)

    @property
    def count(self):
        try:
            return self.object_list.count()
        except (AttributeError, TypeError):
            return len(self.object_list)

    @property
    def num_pages(self):
        if self.count == 0 and not self.allow_empty_first_page:
            return 0

        hits = max(1, self.count - self.orphans)
        return int(ceil(hits / float(self.per_page)))

    @property
    def page_range(self):
        return range(1, self.num_pages + 1)

    