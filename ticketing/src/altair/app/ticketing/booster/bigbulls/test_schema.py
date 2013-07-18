# -*- coding:utf-8 -*-
import unittest
from webob.multidict import MultiDict

class SchemaTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.booster.bigbulls.schemas import ExtraForm
        return ExtraForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        target = self._makeOne()
        self.assertTrue(target.validate())

    def test_validate_false_for_kids(self):
        target = self._makeOne(MultiDict())
        target.configure_for_kids(u'18歳未満')
        self.assertFalse(target.validate())

    def test_validate_true_for_kids(self):
        target = self._makeOne(
            MultiDict(parent_first_name=u"名", 
                      parent_last_name=u"姓", 
                      parent_first_name_kana=u"メイ", 
                      parent_last_name_kana=u"セイ", 
                      relationship=u"父"
                      ))
        target.configure_for_kids(u'18歳未満')
        self.assertTrue(target.validate())

    def test_validate_false_for_authentic_uniform(self):
        target = self._makeOne(MultiDict())
        target.configure_for_authentic_uniform()
        self.assertFalse(target.validate())

    def test_validate_true_for_authentic_uniform(self):
        target = self._makeOne(
            MultiDict(authentic_uniform_no=u"20", 
                      authentic_uniform_size="4L", 
                      authentic_uniform_name=u"NAME", 
                      authentic_uniform_color="red", 
                      ))
        target.configure_for_authentic_uniform()
        self.assertTrue(target.validate())

    def test_validate_false_for_replica_uniform(self):
        target = self._makeOne(MultiDict())
        target.configure_for_replica_uniform()
        self.assertFalse(target.validate())

    def test_validate_true_for_replica_uniform(self):
        target = self._makeOne(
            MultiDict(replica_uniform_size="4L"))
        target.configure_for_replica_uniform()
        self.assertTrue(target.validate())

    def test_validate_false_for_t_shirts_size(self):
        target = self._makeOne(MultiDict())
        target.configure_for_t_shirts_size()
        self.assertFalse(target.validate())

    def test_validate_true_for_t_shirts_size(self):
        target = self._makeOne(
            MultiDict(t_shirts_size="3L"))
        target.configure_for_t_shirts_size()
        self.assertTrue(target.validate())


if __name__ == "__main__":
    unittest.main()
