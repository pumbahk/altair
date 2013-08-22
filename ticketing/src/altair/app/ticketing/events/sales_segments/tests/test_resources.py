import unittest
from pyramid import testing


class SalesSegmentEditorTests(unittest.TestCase):

    def _getTarget(self):
        from ..resources import SalesSegmentEditor
        return SalesSegmentEditor

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_init(self):
        sales_segment_group = testing.DummyModel()
        form = testing.DummyModel()

        target = self._makeOne(sales_segment_group, form)

        self.assertEqual(target.sales_segment_group, sales_segment_group)
        self.assertEqual(target.form, form)

    def test_apply_changes_use_default(self):
        from datetime import datetime
        sales_segment_group = testing.DummyModel(
            start_at=datetime(2013, 8, 31)
        )
        form = DummyForm(
            fields=[
                testing.DummyModel(_name="start_at"),
                testing.DummyModel(_name="use_default_start_at", data=True),
            ],
        )

        target = self._makeOne(sales_segment_group, form)
        
        obj = testing.DummyModel()
        result = target.apply_changes(obj)

        self.assertEqual(result, obj)
        self.assertTrue(result.use_default_start_at)
        self.assertEqual(result.start_at, datetime(2013, 8, 31))

    def test_apply_changes_use_form(self):
        from datetime import datetime
        sales_segment_group = testing.DummyModel(
        )
        form = DummyForm(
            fields=[
                testing.DummyModel(_name="start_at", data=datetime(2013, 8, 31)),
                testing.DummyModel(_name="use_default_start_at", data=False),
            ],
        )

        target = self._makeOne(sales_segment_group, form)
        
        obj = testing.DummyModel()
        result = target.apply_changes(obj)

        self.assertEqual(result, obj)
        self.assertFalse(result.use_default_start_at)
        self.assertEqual(result.start_at, datetime(2013, 8, 31))

class DummyForm(dict):
    def __init__(self, fields):
        for field in fields:
            self[field._name] = field
            setattr(self, field._name, field)
        self.fields = fields

    def __iter__(self):
        return iter(self.fields)
