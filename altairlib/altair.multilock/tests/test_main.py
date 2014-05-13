#-*- coding: utf-8 -*-
from unittest import TestCase



class MultiLockTest(TestCase):
    def test_it(self):
        from altair.multilock import MultiStartLock, AlreadyStartUpError
        from altair.multilock.lock import GRASP, NOT_GRASP


        class GraspLock(MultiStartLock):
            def get_lock(self):
                self.locked = True
                return GRASP

            def release_lock(self):
                self.locked = False
                return None

        class NotGraspLock(MultiStartLock):
            def get_lock(self):
                self.locked = True
                return NOT_GRASP

            def release_lock(self):
                self.locked = False
                return None

        with GraspLock('test') as lock:
            self.assertTrue(lock.locked)
        self.assertTrue(not lock.locked)

        with self.assertRaises(AlreadyStartUpError):
            with NotGraspLock('test') as lock:
                pass
