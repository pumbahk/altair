# -*- coding: utf-8 -*-

import logging
import six
from collections import OrderedDict, Sequence
from math import ceil

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from .settings import api_settings
from .utils import remove_url_query_param, replace_url_query_param

logger = logging.getLogger(__name__)

class InvalidPage(Exception):
    pass

class PageNotAnInteger(InvalidPage):
    pass

class EmptyPage(InvalidPage):
    pass

def _positive_int(integer_str, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    :param integer_str: str
    :param strict: bool
    :param cutoff: int
    :return:
    """
    ret = int(integer_str)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        ret = min(ret, cutoff)
    return ret

class Paginator(object):

    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page = int(per_page)
        self.orphans = int(orphans)
        self.allow_empty_first_page = allow_empty_first_page

    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger("That page number is not integer.")
        if number < 1:
            raise EmptyPage("That page is less than 1.")
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage("That page contains no results.")
        return number

    def get_page(self, number):
        """Return a valid page, even if the page argument isn't a number or ins't in range."""
        try:
            number = self.validate_number(number)
        except PageNotAnInteger:
            number = 1
        except EmptyPage:
            number = self.num_pages
        return self.page(number)

    def page(self, number):
        """Return a page object for the given 1-based number."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return self._get_page(self.object_list[bottom:top], number, self)

    def _get_page(self, *args, **kwargs):
        """
        Return an instance of a single page
        """
        return Page(*args, **kwargs)

    @reify
    def count(self):
        """Return the total number of objects, across all pages."""
        try:
            return self.object_list.count()
        except (AttributeError, TypeError):
            # AttributeError if object_list has no count() method.
            # TypeError if object_list.count() requires argument.
            return len(self.object_list)

    @reify
    def num_pages(self):
        if self.count == 0 and not self.allow_empty_first_page:
            return 0
        hits = max(1, self.count - self.orphans)
        return int(ceil(hits / float(self.per_page)))

    @property
    def page_range(self):
        """
        Return a 1-based ragne of pages for iterating through within
        a template for loop
        """
        return range(1, self.num_pages + 1)

class Page(Sequence):

    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.paginator.num_pages)

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        if not isinstance(index, (int, slice)):
            raise TypeError
        if not isinstance(self.object_list, list):
            self.object_list = list(self.object_list)
        return self.object_list[index]

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_next() or self.has_previous()

    def next_page_number(self):
        return self.paginator.validate_number(self.number + 1)

    def previous_page_number(self):
        return self.paginator.validate_number(self.number - 1)

    def start_index(self):
        """
        Return the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    def end_index(self):
        """
        Return the 1-based index of the last object on this page.
        relative to total objects in the paginator.
        """
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page

class BasePagination(object):

    def paginate_query(self, query, request):
        raise NotImplementedError('paginate_query must be implemented.')

    def get_paginated_response(self, data):
        raise NotImplementedError('get_paginated_response must be implemented.')

class PageNumberPagination(BasePagination):
    # The default page size.
    # Defaults to `None`, meaning pagination is disable
    page_size = api_settings.page_size
    paginator_class = Paginator

    # Allow clients to control the page size using this query parameter.
    # Defaults to `None`.
    page_query_param = 'page'

    # Client can control the page size using this query parameter.
    # Default is 'None'. Set to eg 'page_size' to enable usage.
    page_size_query_param = 'page_size'

    # Set to an integer to limit the maximum page size the client may request.
    # Only relevant if `page_query_param` has also been set.
    max_page_size = 100

    last_page_strings = ('last', )

    def paginate_query(self, query, request):
        """
        Paginate a query if required, either returning a page object,
        or `None` if pagination is not configured for this view
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.paginator_class(query, page_size)
        page_number = request.params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            raise HTTPNotFound(
                "Invalid page '{page_number}': {message}"
                    .format(
                    page_number=page_number,
                    message=six.text_type(exc)
                )
            )

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(json=OrderedDict([
            ('count', self.page.paginator.count),
            ('page_size', self.page_size),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_range', self.page.paginator.page_range),
            ('data', data)
        ]))

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                self.page_size = _positive_int(
                    request.params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.get_url_root()
        page_number = self.page.next_page_number()
        return replace_url_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.get_url_root()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_url_query_param(url, self.page_query_param)
        return replace_url_query_param(url, self.page_query_param, page_number)

    def get_url_root(self):
        return self.request.current_route_url()
