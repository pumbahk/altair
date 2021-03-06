# -*- coding:utf-8 -*-
import unittest
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest

class ClientFormTests(unittest.TestCase):
    def _getTarget(self):
        from .. import schemas
        return schemas.ClientForm

    def _makeOne(self, *args, **kwargs):
        from datetime import datetime
        return self._getTarget()(*args, **kwargs)

    def _params(self, **kwargs):
        from webob.multidict import MultiDict
        return MultiDict(kwargs)

    def test_invalid(self):
        context = testing.DummyResource(
            request=testing.DummyRequest(
                organization=testing.DummyModel(code=u"RT"),
            ),
            cart_setting=testing.DummyModel(type=u"fc"),
        )
        data = self._params(
            last_name=u'テスト',
            last_name_kana=u'テスト',
            first_name=u'テスト',
            first_name_kana=u'テスト',
            #tel_1=u"01234567899",
            fax=u"01234567899",
            zip=u'1234567',
            prefecture=u'東京都',
            city=u'渋谷区',
            address_1=u"代々木１丁目",
            address_2=u"森京ビル",
            sex=u"1",
            email_1=u"test@example.com",
            #email_1_confirm=u"test@example.com",
            email_2=u"test2@example.com",
            #email_2_confirm=u"test2@example.com",
        )
        target = self._makeOne(formdata=data, context=context)
        self.assertFalse(target.validate())
        self.assertIn('tel_1', target.errors)
        self.assertIn('email_1', target.errors)
        self.assertIn('email_2', target.errors)

    def test_it(self):
        context = testing.DummyResource(
            request=testing.DummyRequest(
                organization=testing.DummyModel(code=u"RT"),
            ),
            cart_setting=testing.DummyModel(type=u"fc"),
        )
        data = self._params(**{
            "last_name": u'テスト',
            "last_name_kana": u'テスト',
            "first_name": u'テスト',
            "first_name_kana": u'テスト',
            "tel_1": u"01234567899",
            "fax": u"01234567899",
            "zip": u'1234567',
            "prefecture": u'東京都',
            "city": u'渋谷区',
            "address_1": u"代々木１丁目",
            "address_2": u"森京ビル",
            "sex": u"1",
            "email_1": u"test@example.com",
            "email_1_confirm": u"test@example.com",
            "email_2": u"test2@example.com",
            "email_2_confirm": u"test2@example.com",
            "birthday.year": u"1970",
            "birthday.month": u"01",
            "birthday.day": u"01",
            })
        target = self._makeOne(formdata=data, context=context)
        result = target.validate()
        self.assertTrue(result)
