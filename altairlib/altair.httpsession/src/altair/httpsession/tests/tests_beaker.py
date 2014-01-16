import mock
from unittest import TestCase

class BeakerHTTPSessionBackendFactoryTest(TestCase):
    def _getTarget(self):
        from ..beaker import factory
        return factory

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @mock.patch('beaker.cache.clsmap')
    def test_load_no_key(self, clsmap):
        from webob.request import Request
        from ..exceptions import NoSuchSession
        namespace = mock.MagicMock()
        clsmap.__getitem__ = lambda *args: namespace
        request = Request({})
        retval = self._callFUT(request, type='X', aux_arg1='AAA')
        def raise_exception(*args, **kwargs):
            raise KeyError()
        namespace.return_value.__getitem__ = raise_exception
        with self.assertRaises(NoSuchSession):
            retval.load('ID')
        namespace.return_value.acquire_read_lock.assert_called()
        namespace.return_value.release_read_lock.assert_called()
        namespace.assert_called_with(namespace='ID', aux_arg1='AAA')

    @mock.patch('beaker.cache.clsmap')
    def test_load_valid(self, clsmap):
        from webob.request import Request
        namespace = mock.MagicMock()
        clsmap.__getitem__ = lambda *args: namespace
        request = Request({})
        retval = self._callFUT(request, type='X', aux_arg1='AAA')
        retval.load('ID')
        namespace.return_value.acquire_read_lock.assert_called()
        namespace.return_value.release_read_lock.assert_called()
        namespace.return_value.__getitem__.assert_called_with('session')
        namespace.assert_called_with(namespace='ID', aux_arg1='AAA')

    @mock.patch('beaker.cache.clsmap')
    def test_load_timeout_no_expire(self, clsmap):
        from webob.request import Request
        from datetime import datetime
        namespace = mock.MagicMock()
        clsmap.__getitem__ = lambda *args: namespace
        request = mock.Mock()
        request.current_time = datetime.fromtimestamp(0)
        retval = self._callFUT(request, type='X', timeout=1, aux_arg1='AAA')
        namespace.return_value.__getitem__.return_value = { '_accessed_time': 0 }
        retval.load('ID')
        namespace.return_value.acquire_read_lock.assert_called()
        namespace.return_value.release_read_lock.assert_called()
        namespace.return_value.__getitem__.assert_called_with('session')
        namespace.assert_called_with(namespace='ID', aux_arg1='AAA')

    @mock.patch('beaker.cache.clsmap')
    def test_load_timeout_expire(self, clsmap):
        from datetime import datetime
        from ..exceptions import SessionExpired
        namespace = mock.MagicMock()
        clsmap.__getitem__ = lambda *args: namespace
        request = mock.Mock()
        request.current_time = datetime.fromtimestamp(2)
        retval = self._callFUT(request, type='X', timeout=1, aux_arg1='AAA')
        namespace.return_value.__getitem__.return_value = { '_accessed_time': 0 }
        with self.assertRaises(SessionExpired):
            retval.load('ID')
        namespace.return_value.acquire_read_lock.assert_called()
        namespace.return_value.release_read_lock.assert_called()
        namespace.return_value.__getitem__.assert_called_with('session')
        namespace.assert_called_with(namespace='ID', aux_arg1='AAA')

    @mock.patch('beaker.cache.clsmap')
    def test_save_new(self, clsmap):
        from datetime import datetime
        from ..exceptions import SessionExpired
        namespace = mock.MagicMock()
        clsmap.__getitem__ = lambda *args: namespace
        request = mock.Mock()
        request.current_time = datetime.fromtimestamp(12345678.0)
        retval = self._callFUT(request, type='X', timeout=1, aux_arg1='AAA')
        namespace.return_value.__contains__.return_value = False
        namespace.return_value.__getitem__.return_value = None
        data = { 'FOO': 'BAR' }
        retval.save('ID', data)
        namespace.assert_called_with(namespace='ID', aux_arg1='AAA')
        namespace.return_value.acquire_write_lock.assert_called()
        namespace.return_value.release_write_lock.assert_called()
        namespace.return_value.set_value.assert_called_with(
            'session',
            { '_creation_time': 12345678.0, '_accessed_time': 12345678.0, 'FOO': 'BAR' },
            12345679)
        self.assertEqual(data['_creation_time'], 12345678.0)
        self.assertEqual(data['_accessed_time'], 12345678.0)

    @mock.patch('beaker.cache.clsmap')
    def test_save_existing(self, clsmap):
        from datetime import datetime
        from ..exceptions import SessionExpired
        namespace = mock.MagicMock()
        clsmap.__getitem__ = lambda *args: namespace
        request = mock.Mock()
        request.current_time = datetime.fromtimestamp(12345678.0)
        retval = self._callFUT(request, type='X', timeout=1, aux_arg1='AAA')
        namespace.return_value.__contains__.return_value = True
        namespace.return_value.__getitem__.return_value = {}
        data = { 'FOO': 'BAR' }
        retval.save('ID', data)
        namespace.assert_called_with(namespace='ID', aux_arg1='AAA')
        namespace.return_value.acquire_write_lock.assert_called()
        namespace.return_value.release_write_lock.assert_called()
        namespace.return_value.set_value.assert_called_with(
            'session',
            { '_accessed_time': 12345678.0, 'FOO': 'BAR' },
            12345679)
        self.assertTrue('_creation_time' not in data)
        self.assertEqual(data['_accessed_time'], 12345678.0)

    @mock.patch('beaker.cache.clsmap')
    def test_timeout_relative(self, clsmap):
        from datetime import datetime
        from ..exceptions import SessionExpired
        namespace = mock.MagicMock()
        clsmap.__getitem__ = lambda *args: namespace
        request = mock.Mock()
        request.current_time = datetime.fromtimestamp(12345678.0)
        retval = self._callFUT(request, type='X', timeout=1, backend_always_assumes_timeout_to_be_relative=True, aux_arg1='AAA')
        namespace.return_value.__contains__.return_value = False
        namespace.return_value.__getitem__.return_value = None
        data = { 'FOO': 'BAR' }
        retval.save('ID', data)
        namespace.return_value.set_value.assert_called_with(
            'session',
            { '_creation_time': 12345678.0, '_accessed_time': 12345678.0, 'FOO': 'BAR' },
            1)


