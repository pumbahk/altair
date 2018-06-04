# -*- coding:utf-8 -*-
import os
import sys
from cgi import parse_header
from os.path import dirname

from pyramid_mailer import get_mailer
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.message import Attachment


class MailTestMixin(object):
    def set_dummy_conf_ini_file_path(self):
        """セットしたダミーのiniファイルのパスは、送信対象のホワイトリスト機能（get_white_list_recipient(self, request)）で使用"""
        bin_test_ticketing = sys.argv[0]
        deploy_dir = dirname(dirname(dirname(bin_test_ticketing)))
        self.config.registry.settings.update({'deploy_dir': deploy_dir})

        paths = [deploy_dir, 'test', 'conf', 'altair.dummy.ini']
        dummy_conf_ini_path = os.sep.join(paths)
        self.config.registry.settings.update({'__file__': dummy_conf_ini_path})

    def registerDummyMailer(self):
        self.config.registry.unregisterUtility(get_mailer(self.config.registry), IMailer)
        self.config.include('pyramid_mailer.testing')

    def assertBodyContains(self, needle, haystack, message=None):
        if isinstance(haystack, Attachment):
            ct, ctparams = parse_header(haystack.content_type)
            haystack = haystack.data.decode(ctparams.get('charset', 'UTF-8'))
        self.assertIn(needle, haystack, message)

    def assertBodyDoesNotContain(self, needle, haystack, message=None):
        if isinstance(haystack, Attachment):
            ct, ctparams = parse_header(haystack.content_type)
            haystack = haystack.data.decode(ctparams.get('charset', 'UTF-8'))
        self.assertNotIn(needle, haystack, message)
