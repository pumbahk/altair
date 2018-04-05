# -*- coding: utf-8 -*-

from unittest import TestCase

from altair.restful_framework import utils

class UtilsTests(TestCase):

    def test_replace_query_param(self):
        expected = 'http://test.jp?name=replaced_test'
        assert utils.replace_url_query_param('http://test.jp', 'name', 'replaced_test') == expected
        assert utils.replace_url_query_param('http://test.jp?name=test', 'name', 'replaced_test') == expected

    def test_remove_query_param(self):
        expected = 'http://test.jp'
        assert utils.remove_url_query_param('http://test.jp?name=test', 'name') == expected