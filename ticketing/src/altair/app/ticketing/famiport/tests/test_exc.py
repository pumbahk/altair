# -*- coding: utf-8 -*-
from unittest import TestCase


class FamiPortAPIErrorTest(TestCase):
    def _get_target_class(self):
        from ..exc import FamiPortAPIError as klass
        return klass

    def _create(self, *args, **kwds):
        klass = self._get_target_class()
        return klass('TEST')

    def _raise(self, *args, **kwds):
        obj = self._create(*args, **kwds)
        raise obj

    def test_it(self):
        from ..exc import FamiPortAPIError
        with self.assertRaises(FamiPortAPIError):
            self._raise()

    def test_repr(self):
        obj = self._create('TEST')
        repr(obj)

    def test_str(self):
        obj = self._create('TEST')
        str(obj)

    def test_nested_exc_info(self):
        from ..exc import FamiPortAPIError
        try:
            try:
                raise ValueError('first raise')
            except ValueError:
                raise FamiPortAPIError('second raise')
        except FamiPortAPIError as err:
            str(err)
