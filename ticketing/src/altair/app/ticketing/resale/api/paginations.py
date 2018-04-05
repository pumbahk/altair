# -*- coding: utf-8 -*-

from altair.restful_framework.pagination import PageNumberPagination

class ResaleSegmentPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ResaleRequestPageNumberPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100