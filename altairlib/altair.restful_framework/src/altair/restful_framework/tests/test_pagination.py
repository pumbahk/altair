# -*- coding: utf-8 -*-

from mock import Mock
from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound
from unittest import TestCase

from altair.restful_framework import pagination
from altair.restful_framework.pagination import Page, Paginator, InvalidPage, PageNotAnInteger, EmptyPage


class ValidAdjacentNumsPage(Page):

    def next_page_number(self):
        if not self.has_next():
            return None
        return super(ValidAdjacentNumsPage, self).next_page_number()

    def previous_page_number(self):
        if not self.has_previous():
            return None
        return super(ValidAdjacentNumsPage, self).previous_page_number()


class ValidAdjacentNumsPaginator(Paginator):

    def _get_page(self, *args, **kwargs):
        return ValidAdjacentNumsPage(*args, **kwargs)


class PaginatorTests(TestCase):

    def check_attr(self, name, paginator, expected, params, coerce=None):
        gotattr = getattr(paginator, name)

        if coerce is not None:
            gotattr = coerce(gotattr)

        self.assertEqual(
            expected, gotattr,
            "For {}, expected {} but got {}. Paginator parameters were {}" \
            .format(name, expected, gotattr, params)
        )

    def check_paginator(self, params, output):
        count, num_pages, page_range = output
        paginator = Paginator(*params)

        self.check_attr('count', paginator, count, params)
        self.check_attr('num_pages', paginator, num_pages, params)
        self.check_attr('page_range', paginator, page_range, params, coerce=list)

    def test_paginator(self):
        nine = range(1, 10)
        ten = nine + [10]
        eleven = ten + [11]

        tests = (
            # Each item is two tuples:
            #     First tuple is Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is resulting Paginator attributes - count,
            #         num_pages, and page_range.
            # Ten items, varying orphans, no empty first page.
            ((ten, 4, 0, False), (10, 3, [1, 2, 3])),
            ((ten, 4, 1, False), (10, 3, [1, 2, 3])),
            ((ten, 4, 2, False), (10, 2, [1, 2])),
            ((ten, 4, 5, False), (10, 2, [1, 2])),
            ((ten, 4, 6, False), (10, 1, [1])),
            # Ten items, varying orphans, allow empty first page.
            ((ten, 4, 0, True), (10, 3, [1, 2, 3])),
            ((ten, 4, 1, True), (10, 3, [1, 2, 3])),
            ((ten, 4, 2, True), (10, 2, [1, 2])),
            ((ten, 4, 5, True), (10, 2, [1, 2])),
            ((ten, 4, 6, True), (10, 1, [1])),
            # One item, varying orphans, no empty first page.
            (([1], 4, 0, False), (1, 1, [1])),
            (([1], 4, 1, False), (1, 1, [1])),
            (([1], 4, 2, False), (1, 1, [1])),
            # One item, varying orphans, allow empty first page.
            (([1], 4, 0, True), (1, 1, [1])),
            (([1], 4, 1, True), (1, 1, [1])),
            (([1], 4, 2, True), (1, 1, [1])),
            # Zero items, varying orphans, no empty first page.
            (([], 4, 0, False), (0, 0, [])),
            (([], 4, 1, False), (0, 0, [])),
            (([], 4, 2, False), (0, 0, [])),
            # Zero items, varying orphans, allow empty first page.
            (([], 4, 0, True), (0, 1, [1])),
            (([], 4, 1, True), (0, 1, [1])),
            (([], 4, 2, True), (0, 1, [1])),
            # Number if items one less than per_page.
            (([], 1, 0, True), (0, 1, [1])),
            (([], 1, 0, False), (0, 0, [])),
            (([1], 2, 0, True), (1, 1, [1])),
            ((nine, 10, 0, True), (9, 1, [1])),
            # Number if items equal to per_page.
            (([1], 1, 0, True), (1, 1, [1])),
            (([1, 2], 2, 0, True), (2, 1, [1])),
            ((ten, 10, 0, True), (10, 1, [1])),
            # Number if items one more than per_page.
            (([1, 2], 1, 0, True), (2, 2, [1, 2])),
            (([1, 2, 3], 2, 0, True), (3, 2, [1, 2])),
            ((eleven, 10, 0, True), (11, 2, [1, 2])),
            # Number if items one more than per_page with one orphan.
            (([1, 2], 1, 1, True), (2, 1, [1])),
            (([1, 2, 3], 2, 1, True), (3, 1, [1])),
            ((eleven, 10, 1, True), (11, 1, [1])),
            # Non-integer inputs
            ((ten, '4', 1, False), (10, 3, [1, 2, 3])),
            ((ten, '4', 1, False), (10, 3, [1, 2, 3])),
            ((ten, 4, '1', False), (10, 3, [1, 2, 3])),
            ((ten, 4, '1', False), (10, 3, [1, 2, 3])),
        )

        for params, output in tests:
            self.check_paginator(params, output)

    def test_invalid_page_number(self):
        paginator = Paginator([1, 2, 3], 2)
        with self.assertRaises(InvalidPage):
            paginator.page(3)
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number(None)
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number('a')
        with self.assertRaises(EmptyPage):
            paginator.validate_number(-1)
        with self.assertRaises(EmptyPage):
            paginator.validate_number(999)

        paginator = Paginator([], 2)
        self.assertEqual(paginator.validate_number(1), 1)

    def test_paginate_misc_classes(self):
        class CountContainer(object):
            def count(self):
                return 42

        paginator = Paginator(CountContainer(), 10)
        self.assertEqual(paginator.count, 42)
        self.assertEqual(paginator.num_pages, 5)
        self.assertEqual(list(paginator.page_range), [1, 2, 3, 4, 5])


        class LenContainer(object):
            def __len__(self):
                return 42

        paginator = Paginator(LenContainer(), 10)
        self.assertEqual(paginator.count, 42)
        self.assertEqual(paginator.num_pages, 5)
        self.assertEqual(list(paginator.page_range), [1, 2, 3, 4, 5])

    def check_indices(self, params, page_num, indices):
        paginator = Paginator(*params)
        if page_num == 'first':
            page_num = 1
        elif page_num == 'last':
            page_num = paginator.num_pages

        page = paginator.page(page_num)
        start, end = indices
        msg = ("For {} of page {}, expected {} but got {}. Paginator parameters were: {}")
        self.assertEqual(start, page.start_index(),
                         msg.format('start index', page_num, start, page.start_index(), params))
        self.assertEqual(end, page.end_index(),
                         msg.format('end index', page_num, end, page.end_index(), params))

    def test_page_indices(self):
        ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        tests = (
            # Each item is three tuples:
            #     First tuple is Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is the start and end indexes of the first page.
            #     Third tuple is the start and end indexes of the last page.
            # Ten items, varying per_page, no orphans.
            ((ten, 1, 0, True), (1, 1), (10, 10)),
            ((ten, 2, 0, True), (1, 2), (9, 10)),
            ((ten, 3, 0, True), (1, 3), (10, 10)),
            ((ten, 5, 0, True), (1, 5), (6, 10)),
            # Ten items, varying per_page, with orphans.
            ((ten, 1, 1, True), (1, 1), (9, 10)),
            ((ten, 1, 2, True), (1, 1), (8, 10)),
            ((ten, 3, 1, True), (1, 3), (7, 10)),
            ((ten, 3, 2, True), (1, 3), (7, 10)),
            ((ten, 3, 4, True), (1, 3), (4, 10)),
            ((ten, 5, 1, True), (1, 5), (6, 10)),
            ((ten, 5, 2, True), (1, 5), (6, 10)),
            ((ten, 5, 5, True), (1, 10), (1, 10)),
            # One item, varying orphans, no empty first page.
            (([1], 4, 0, False), (1, 1), (1, 1)),
            (([1], 4, 1, False), (1, 1), (1, 1)),
            (([1], 4, 2, False), (1, 1), (1, 1)),
            # One item, varying orphans, allow empty first page.
            (([1], 4, 0, True), (1, 1), (1, 1)),
            (([1], 4, 1, True), (1, 1), (1, 1)),
            (([1], 4, 2, True), (1, 1), (1, 1)),
            # Zero items, varying orphans, allow empty first page.
            (([], 4, 0, True), (0, 0), (0, 0)),
            (([], 4, 1, True), (0, 0), (0, 0)),
            (([], 4, 2, True), (0, 0), (0, 0)),
        )

        for params, first, last in tests:
            self.check_indices(params, 'first', first)
            self.check_indices(params, 'last', last)

        # When no items and no empty first page, EmptyPage error should be raised.
        with self.assertRaises(EmptyPage):
            self.check_indices(([], 4, 0, False), 1, None)
        with self.assertRaises(EmptyPage):
            self.check_indices(([], 4, 1, False), 1, None)
        with self.assertRaises(EmptyPage):
            self.check_indices(([], 4, 2, False), 1, None)

    def test_page_sequence(self):
        eleven = 'abcdefghijkl'
        page2 = Paginator(eleven, per_page=5, orphans=1).page(2)
        self.assertEqual(len(page2), 5)
        self.assertIn('f', page2)
        self.assertNotIn('k', page2)
        self.assertEqual(''.join(page2), 'fghij')
        self.assertEqual(''.join(reversed(page2)), 'jihgf')

    def test_get_page_hook(self):
        eleven = 'abcdefghijkl'
        paginator = ValidAdjacentNumsPaginator(eleven, per_page=6)
        page1 = paginator.page(1)
        page2 = paginator.page(2)
        self.assertIsNone(page1.previous_page_number())
        self.assertEqual(page1.next_page_number(), 2)
        self.assertEqual(page2.previous_page_number(), 1)
        self.assertIsNone(page2.next_page_number())

    def test_page_range_iterator(self):
        self.assertIsInstance(Paginator([1,2,3], 2).page_range, type(range(0)))

class TestPageNumberPagination(TestCase):

    def setUp(self):
        class TestPagination(pagination.PageNumberPagination):
            page_size = 5

        self.pagination = TestPagination()
        self.data = range(1, 101)

    def paginate_query(self, request):
        return list(self.pagination.paginate_query(self.data, request))

    def get_paginated_data(self, data):
        resp = self.pagination.get_paginated_response(data)
        return resp.json_body

    def get_current_url(self):
        return 'http://test/'

    def test_no_page_number(self):
        request = testing.DummyRequest()
        request.current_route_url = Mock(side_effect=self.get_current_url)
        data = self.paginate_query(request)
        paginated_data = self.get_paginated_data(data)
        assert data == [1, 2, 3, 4, 5]
        assert paginated_data == {
            'count': 100,
            'page_size': 5,
            'next': 'http://test/?page=2',
            'previous': None,
            'page_range': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            'data': [1, 2, 3, 4, 5]
        }

    def test_second_page(self):
        request = testing.DummyRequest()
        request.current_route_url = Mock(side_effect=self.get_current_url)
        request.params['page'] = 2
        data = self.paginate_query(request)
        paginated_data = self.get_paginated_data(data)
        assert data == [6, 7, 8, 9, 10]
        assert paginated_data == {
            'count': 100,
            'page_size': 5,
            'next': 'http://test/?page=3',
            'previous': 'http://test/',
            'page_range': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            'data': [6, 7, 8, 9, 10]
        }

    def test_last_page(self):
        request = testing.DummyRequest()
        request.current_route_url = Mock(side_effect=self.get_current_url)
        request.params['page'] = 'last'
        data = self.paginate_query(request)
        paginated_data = self.get_paginated_data(data)
        assert data == [96, 97, 98, 99, 100]
        assert paginated_data == {
            'count': 100,
            'page_size': 5,
            'next': None,
            'previous': 'http://test/?page=19',
            'page_range': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            'data': [96, 97, 98, 99, 100]
        }

    def test_invalid_page(self):
        request = testing.DummyRequest()
        request.current_route_url = Mock(side_effect=self.get_current_url)
        request.params['page'] = 'abc'
        self.assertRaises(HTTPNotFound, self.paginate_query, request)

class TestPageNumberPaginationOverride(TestCase):

    def setUp(self):
        class OverridePaginator(Paginator):
            count = 1

        class TestPagination(pagination.PageNumberPagination):
            page_size = 5
            paginator_class = OverridePaginator
            page_size_query_param = 'unit'

        self.pagination = TestPagination()
        self.data = range(1, 101)

    def paginate_query(self, request):
        return list(self.pagination.paginate_query(self.data, request))

    def get_paginated_data(self, data):
        resp = self.pagination.get_paginated_response(data)
        return resp.json_body

    def get_current_url(self):
        return 'http://test/'

    def test_no_page_number(self):
        request = testing.DummyRequest()
        request.current_route_url = Mock(side_effect=self.get_current_url)
        data = self.paginate_query(request)
        paginated_data = self.get_paginated_data(data)
        assert data == [1]
        assert paginated_data == {
            'count': 1,
            'page_size': 5,
            'next': None,
            'previous': None,
            'page_range': [1],
            'data': [1]
        }

    def test_invalid_page(self):
        request = testing.DummyRequest()
        request.current_route_url = Mock(side_effect=self.get_current_url)
        request.params['page'] = 'abc'
        self.assertRaises(HTTPNotFound, self.paginate_query, request)

    def test_overridden_page_size_query_param(self):
        request = testing.DummyRequest()
        request.current_route_url = Mock(side_effect=self.get_current_url)
        request.params['unit'] = 1
        data = self.paginate_query(request)
        paginated_data = self.get_paginated_data(data)
        assert data == [1]
        assert paginated_data == {
            'count': 1,
            'page_size': 1,
            'next': None,
            'previous': None,
            'page_range': [1],
            'data': [1]
        }