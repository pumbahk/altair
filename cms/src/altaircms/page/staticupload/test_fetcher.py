# -*- coding:utf-8 -*-
import unittest
import mock

class PageCacheTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.page.staticupload.fetcher import StaticPageCache
        return StaticPageCache

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()({}, *args, **kwargs)

    def test_on_fetching_another__raise_404(self):
        from pyramid.httpexceptions import HTTPNotFound
        cache_key = ":key:"
        target = self._makeOne()
        with self.assertRaises(HTTPNotFound):
            target.on_fetching_another(cache_key)

    def test_on_fetching_self__success_key_and_value_are_set(self):
        cache_key = ":key:"
        def fetch_function(_self, k):
            self.assertEqual(k, ":key:")
            return mock.sentinel.Data

        target = self._makeOne()
        target.on_fetching_self(cache_key, fetch_function)
        self.assertEqual(target.file_data[cache_key], 
                         mock.sentinel.Data)

    def test_on_fetching_self__success_fetching_is_removed(self):
        cache_key = ":key:"
        def fetch_function(_self, k):
            return mock.sentinel.Data

        target = self._makeOne()
        target.fetching = mock.MagicMock()
        with mock.patch("altaircms.page.staticupload.fetcher.datetime") as m:
            m.return_value = mock.sentinel.Now
            target.on_fetching_self(cache_key, fetch_function)

            fetching = target.fetching
            fetching.__setitem__.assert_has_called([mock.call(cache_key, mock.sentinel.Now)])
            fetching.remove_value.assert_called_with_once([mock.call(cache_key)])

    def test_on_fetching_self__EOFError__clear_cache_is_called(self):
        from pyramid.httpexceptions import HTTPNotFound
        cache_key = ":key:"
        def fetch_function(_self, k):
            raise EOFError
        target = self._makeOne()

        with mock.patch.object(target, "clear_cache") as m:
            with self.assertRaises(HTTPNotFound):
                target.on_fetching_self(cache_key, fetch_function)
            m.assert_called_with_once(cache_key)

    def test_on_fetching_self__ValueError__clear_cache_is_called(self):
        from pyramid.httpexceptions import HTTPNotFound
        cache_key = ":key:"
        def fetch_function(_self, k):
            raise ValueError
        target = self._makeOne()

        with mock.patch.object(target, "clear_cache") as m:
            with self.assertRaises(HTTPNotFound):
                target.on_fetching_self(cache_key, fetch_function)
            m.assert_called_with_once(cache_key)

    def test_on_fetching_self__Exception__clear_cache_is_called(self):
        from pyramid.httpexceptions import HTTPNotFound
        cache_key = ":key:"
        def fetch_function(_self, k):
            raise Exception
        target = self._makeOne()

        with mock.patch.object(target, "clear_cache") as m:
            with self.assertRaises(HTTPNotFound):
                target.on_fetching_self(cache_key, fetch_function)
            m.assert_called_with_once(cache_key)

    def test_on_fetching_self__fetched_value_is_None__clear_cache_is_called(self):
        from pyramid.httpexceptions import HTTPNotFound
        cache_key = ":key:"
        def fetch_function(_self, k):
            return None
        target = self._makeOne()

        with mock.patch.object(target, "clear_cache") as m:
            with self.assertRaises(HTTPNotFound):
                target.on_fetching_self(cache_key, fetch_function)
            m.assert_called_with_once(cache_key)
        
    def test_clear_cache__success(self):
        cache_key = ":key:"
        target = self._makeOne()
        target.fetching.remove_value = mock.Mock()

        with mock.patch.object(target.file_data, "remove_value") as m:
            target.clear_cache(cache_key)
            m.assert_called_with_once(cache_key)

        target.fetching.remove_value.assert_called_with_once(cache_key)

    def test_clear_cache__ValueError__do_remove(self):
        cache_key = ":key:"
        target = self._makeOne()
        target.fetching.remove_value = mock.Mock()

        with mock.patch.object(target, "file_data") as m:
            m.remove_value.side_effect = ValueError("insecure string")
            m_file_delete = m._get_value.return_value.namespace.do_remove #hmm

            target.clear_cache(cache_key)
            m.remove_value.assert_called_with_once(cache_key)
            m_file_delete.assert_called_with_once()

        target.fetching.remove_value.assert_called_with_once(cache_key)

    def test_clear_cache__EOFError__do_remove(self):
        cache_key = ":key:"
        target = self._makeOne()
        target.fetching.remove_value = mock.Mock()

        with mock.patch.object(target, "file_data") as m:
            m.remove_value.side_effect = EOFError()
            m_file_delete = m._get_value.return_value.namespace.do_remove #hmm

            target.clear_cache(cache_key)
            m.remove_value.assert_called_with_once(cache_key)
            m_file_delete.assert_called_with_once()

        target.fetching.remove_value.assert_called_with_once(cache_key)    


    def test_clear_cache__Exception__do_remove(self):
        cache_key = ":key:"
        target = self._makeOne()
        target.fetching.remove_value = mock.Mock()

        with mock.patch.object(target, "file_data") as m:
            m.remove_value.side_effect = Exception("insecure string")
            m_file_delete = m._get_value.return_value.namespace.do_remove #hmm

            target.clear_cache(cache_key)
            m.remove_value.assert_called_with_once(cache_key)
            m_file_delete.assert_called_with_once()

        target.fetching.remove_value.assert_called_with_once(cache_key)

if __name__ == "__main__":
    unittest.main()
