# -*- coding:utf-8 -*-
import unittest
import mock

class FileCacheTests(unittest.TestCase):
    def _makeOne(self):
        from altaircms.cachelib import FileCacheStore
        return FileCacheStore({})

    def test_it(self):
        target = self._makeOne()
        self.assertIsNone(target.get(":k:"))
        target.set(":k:", ":v:")
        self.assertEquals(target.get(":k:"), ":v:")

    @mock.patch("altaircms.cachelib.FileCacheStore.get_cache")
    def test_get_broken_cache__clear_cache_is_called(self, mget_cache):
        def getitem(s, k):
            raise ValueError("insecure string")
        mget_cache.return_value.__getitem__ = getitem
        target = self._makeOne()
        k = ":k:"
        with mock.patch("altaircms.cachelib.clear_cache") as m:
            target.get(k)
            m.assert_called_once_with(mget_cache.return_value, target.k)

    @mock.patch("altaircms.cachelib.FileCacheStore.get_cache")
    def test_set_broken_cache__clear_cache_is_called(self, mget_cache):
        def setitem(s, k, v):
            raise ValueError("insecure string")
        mget_cache.return_value.__setitem__ = setitem
        tarset = self._makeOne()
        k = ":k:"
        with mock.patch("altaircms.cachelib.clear_cache") as m:
            tarset.set(k, ":v:")
            m.assert_called_once_with(mget_cache.return_value, tarset.k)


class ClearCacheTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.cachelib import clear_cache
        return clear_cache(*args, **kwargs)

    def test_it(self):
        from altaircms.cachelib import FileCacheStore
        cache = FileCacheStore({"expire": 3000})
        cache.set(":k:", ":v:")
        self.assertEqual(cache.get(":k:"), ":v:")

        self._callFUT(cache.get_cache(":k:"), cache.k)
        self.assertIsNone(cache.get(":k:"))


class ForAtomicTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from altaircms.cachelib import ForAtomic
        return ForAtomic(*args, **kwargs)

    def test_it(self):
        target = self._makeOne({"expire": 3000})
        k = ":k1:"

        target.end_requesting(k)
        self.assertFalse(target.is_requesting(k))
        target.start_requesting(k)
        self.assertTrue(target.is_requesting(k))
        target.end_requesting(k)
        self.assertFalse(target.is_requesting(k))

    def test_context_manager(self):
        target = self._makeOne({"expire": 3000})

        k = ":k2:"

        with target.atomic(k):
            self.assertTrue(target.is_requesting(k))
        self.assertFalse(target.is_requesting(k))
