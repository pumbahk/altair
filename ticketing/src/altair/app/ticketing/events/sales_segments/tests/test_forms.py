# -*- coding:utf-8 -*-

import unittest
from webob.multidict import MultiDict

class EditSalesSegmentFormTests(unittest.TestCase):
    def setUp(self):
        import altair.app.ticketing.core.models
        import sqlalchemy.orm
        sqlalchemy.orm.configure_mappers()

    def _getTarget(self):
        from ..forms import EditSalesSegmentForm
        return EditSalesSegmentForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_validate_start_at_use_default(self):
        formdata = MultiDict(
            dict(
                use_default_start_at=True,
                end_at="",
            )
        )
        target = self._makeOne(formdata=formdata)
        target.validate()
        self.assertNotIn('start_at', target.errors)

    def test_validate_start_at_use_form_invalid(self):
        formdata = MultiDict(
            dict(
                start_at="",
                use_default_start_at="on",
                end_at="",
            )
        )
        target = self._makeOne(formdata=formdata)
        target.process()

        target.validate()
        self.assertTrue(target.errors)
        self.assertIn('start_at', target.errors)
        self.assertEqual(target.errors['start_at'], [u"入力してください"])

    def test_validate_start_at_use_form(self):
        formdata = MultiDict(
            dict(
                start_at="2013-08-31 23:59",
                use_default_start_at=False,
                end_at="",
            )
        )
        target = self._makeOne(formdata=formdata)

        target.validate()
        for name, errors in target.errors.items():
            print name,
            for e in errors:
                print e

        self.assertNotIn('start_at', target.errors)
