# -*- coding: utf-8 -*-
from unittest import TestCase
import re


class CooperationViewTest(TestCase):
    def test_create_file_download_response_header(self):
        from ..views import CooperationView
        filename = 'TEST.csv'
        timestamp = True
        CooperationView._create_file_download_response_header(filename, timestamp)
