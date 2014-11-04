# -*- coding: utf-8 -*-
from unittest import TestCase
from altair.app.ticketing.core.models import (
    Account,
    AugusAccount,
    )
from ..operations import (
    PathManager,
    )

class AugusOperationTest(TestCase):
    def setup(self):
        account = Account()
        augus_account = AugusAccount()

    def teardown(self):
        pass


class PathManagerTest(TestCase):
    augus_account_id = 3
    var_dir = 'test'
    send_dir = 'send_dir'
    recv_dir = 'recv_dir'

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
