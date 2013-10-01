# -*- coding:utf-8 -*-

import unittest
from webob.multidict import MultiDict
from pyramid.testing import DummyResource
from mock import Mock

class SalesSegmentFormTests(unittest.TestCase):
    def setUp(self):
        import altair.app.ticketing.core.models
        import sqlalchemy.orm
        sqlalchemy.orm.configure_mappers()

    def _getTarget(self):
        from ..forms import SalesSegmentForm
        return SalesSegmentForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_validate_start_at_use_default(self):
        formdata = MultiDict(
            dict(
                use_default_start_at=True,
                end_at="",
            )
        )
        context = DummyResource(
            organization=Mock(accounts=[Mock()]),
            event=Mock(sales_segment_groups=[]),
            sales_segment_group=None
            )
        target = self._makeOne(formdata=formdata, context=context)
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
        context = DummyResource(
            organization=Mock(accounts=[Mock()]),
            event=Mock(sales_segment_groups=[]),
            sales_segment_group=None
            )
        target = self._makeOne(formdata=formdata, context=context)
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
        context = DummyResource(
            organization=Mock(accounts=[Mock()]),
            event=Mock(sales_segment_groups=[]),
            sales_segment_group=None
            )
        target = self._makeOne(formdata=formdata, context=context)

        target.validate()
        for name, errors in target.errors.items():
            print name,
            for e in errors:
                print e.encode('utf-8')

        self.assertNotIn('start_at', target.errors)
