# -*- coding: utf-8 -*-
from unittest import TestCase
import os
import shutil
from altair.app.ticketing.core.models import (
    Account,
    AugusAccount,
    )
from ..operations import (
    PathManager,
    )
from altair.app.ticketing.mails.testing import MailTestMixin
from pyramid import testing

class AugusOperationTest(TestCase):
    def setup(self):
        self.account = Account()
        self.augus_account = AugusAccount()

    def teardown(self):
        pass


class PathManagerTest(TestCase, MailTestMixin):
    def setUp(self):
        self.config = testing.setUp()
        self.set_dummy_conf_ini_file_path()
        self.augus_account_id = '3'
        self.var_dir = os.sep.join([self.config.registry.settings.deploy_dir, 'test'])
        self.send_dir = 'send_dir'
        self.recv_dir = 'recv_dir'
        self.test_dir_top = os.sep.join([self.var_dir, self.augus_account_id])

        # 過去のテストの中断など、何らかの理由でテストディレクトリが残っていれば削除
        if os.path.isdir(self.test_dir_top):
            shutil.rmtree(self.test_dir_top)

    def tearDown(self):
        # テストで作成されたディレクトリの削除
        shutil.rmtree(self.test_dir_top)

    def get_target(self):
        augus_account = AugusAccount()
        augus_account.id = self.augus_account_id
        augus_account.send_dir = self.send_dir
        augus_account.recv_dir = self.recv_dir
        var_dir = self.var_dir
        return PathManager(augus_account, var_dir)

    def test_it(self):
        mgr = self.get_target()
        self.assertEqual(mgr.work_dir, '{}/{}'.format(self.var_dir, self.augus_account_id))
        self.assertEqual(mgr.send_dir_staging, '{}/{}/{}/staging'.format(self.var_dir, self.augus_account_id, self.send_dir))
        self.assertEqual(mgr.send_dir_pending, '{}/{}/{}/pending'.format(self.var_dir, self.augus_account_id, self.send_dir))
        self.assertEqual(mgr.recv_dir_staging, '{}/{}/{}/staging'.format(self.var_dir, self.augus_account_id, self.recv_dir))
        self.assertEqual(mgr.recv_dir_pending, '{}/{}/{}/pending'.format(self.var_dir, self.augus_account_id, self.recv_dir))
