# -*- coding:utf-8 -*-
import unittest

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
import sqlalchemy.orm as orm

Base = declarative_base()
class Parent(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime)
    __tablename__ = "parent"

class Child(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(Parent.id))
    parent = orm.relationship(Parent, backref="children", uselist=False)
    created_at = sa.Column(sa.DateTime)
    __tablename__ = "child"

class NullModelTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.modellib import null_model
        return null_model(*args, **kwargs)

    def test_attributes__parent(self):
        parent = self._callFUT(Parent)
        self.assertTrue(hasattr(parent, "id"))
        self.assertTrue(hasattr(parent, "children"))
        self.assertFalse(hasattr(parent, "parent"))

    def test_attributes__child(self):
        child = self._callFUT(Child)
        self.assertTrue(hasattr(child, "id"))
        self.assertFalse(hasattr(child, "children"))
        self.assertTrue(hasattr(child, "parent"))

    def test_error__access_missing_attribute(self):
        parent = self._callFUT(Parent)
        parent.id
        with self.assertRaises(AttributeError):
            parent.foo

    def test_coerce(self):
        parent = self._callFUT(Parent)
        self.assertEqual(int(parent), 0)
        self.assertTrue(isinstance(str(parent), str)) #stringに変換できるかどうかだけ
        self.assertFalse(parent)

    def test_display_datetime(self):
        parent = self._callFUT(Parent)

        from altaircms.helpers.base import jdatetime
        self.assertTrue(isinstance(jdatetime(parent.created_at), unicode)) #errorがでないことだけ


class FirstOrNullModelTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.modellib import first_or_nullmodel
        return first_or_nullmodel(*args, **kwargs)

    def test_it__get_first(self):
        parent = Parent()
        child = Child()
        parent.children.append(child)
        result = self._callFUT(parent, "children")

        self.assertEqual(result, child)

    def test_it__empty_children(self):
        parent = Parent()
        child = Child()
        result = self._callFUT(parent, "children")

        self.assertNotEqual(result, child)

        from altaircms.modellib import QuietMock
        self.assertTrue(isinstance(result, QuietMock))
