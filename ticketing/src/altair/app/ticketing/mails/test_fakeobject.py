# -*- coding:utf-8 -*-
import unittest

class FakeObjectTest(unittest.TestCase):
    def _makeOne(*args, **kwargs):
        from altair.app.ticketing.mails.fake import FakeObject
        return FakeObject(*args, **kwargs)

    def test_it(self):
        target = self._makeOne()
        target.a.b.c
        target.f().g().h()
        target.f(target.x==target.y)

    # def test_format(self):
    #     target = self._makeOne()
    #     u"{d.day:02}".format(d=target)

if __name__ == "__main__":
    unittest.main()
