# -*- coding:utf-8 -*-
import unittest
import mock
from mock import sentinel as S

class DummyFetcher(object):
    pass

def make_atomic(status):
    from altaircms.cachelib import DummyAtomic
    return DummyAtomic(status)

def make_cache(**kwargs):
    from altaircms.cachelib import OnMemoryCacheStore
    cache = OnMemoryCacheStore()
    for k, v in kwargs.items():
        cache.set(k, v)
    return cache

class PageCacheTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.page.staticupload.fetcher import CachedFetcher
        return CachedFetcher

    def _makeOne(self, fetcher, cache, atomic):
        return self._getTarget()(fetcher, cache, atomic)

    def test_another_process_is_requesting__throgh_cache(self):
        fetcher = mock.Mock()
        cache = make_cache()
        atomic = make_atomic(status=True)
        target = self._makeOne(fetcher, cache, atomic)
        target.fetch(S.url, S.path)
        fetcher.fetch.assert_called_with_once(S.url, S.path)

    def test_fetching_success__value_are_set(self):
        fetcher = mock.MagicMock()
        fetcher.fetch.return_value = S.FETCHED_VALUE
        S.FETCHED_VALUE.code = 200

        atomic = make_atomic(status=False)
        cache = make_cache()
        target = self._makeOne(fetcher, cache, atomic)
        def dummy_fetch(k, url, path):
            self.assertEquals(k, target.make_key(url, path))
            return fetcher.fetch(url, path)
        target._fetch = dummy_fetch
        result = target.fetch(S.url, S.path)

        self.assertEquals(result, S.FETCHED_VALUE)
        self.assertEquals(cache.get(target.make_key(S.url, S.path)), S.FETCHED_VALUE)

    def test_fetching_success__but_code_is_not_200(self):
        fetcher = mock.MagicMock()
        fetcher.fetch.return_value = S.FETCHED_VALUE
        S.FETCHED_VALUE.code = 302

        atomic = make_atomic(status=False)
        cache = make_cache()
        target = self._makeOne(fetcher, cache, atomic)
        def dummy_fetch(k, url, path):
            self.assertEquals(k, target.make_key(url, path))
            return fetcher.fetch(url, path)
        target._fetch = dummy_fetch

        from .fetcher import StaticPageRequestFailure
        with self.assertRaises(StaticPageRequestFailure):
            target.fetch(S.url, S.path)


    def test_if_hitting_cache(self):
        fetcher = mock.MagicMock()
        atomic = make_atomic(status=False)
        cache = make_cache()
        target = self._makeOne(fetcher, cache, atomic)
        cache.set(target.make_key(S.url, S.path), S.CACHED_VALUE)

        result = target.fetch(S.url, S.path)
        self.assertEquals(result, S.CACHED_VALUE)



if __name__ == "__main__":
    unittest.main()
