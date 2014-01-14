import mock
from unittest import TestCase

class GetNowFromRequestTest(TestCase):
    def _getTarget(self):
        from ..api import get_now_from_request
        return get_now_from_request

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)
    
    def test_without_altair_now(self):
        from datetime import datetime
        from webob.request import Request
        class fake_datetime(datetime):
            @classmethod
            def now(self):
                return datetime(2013, 1, 1, 0, 0, 0)

        with mock.patch('altair.httpsession.api.datetime.datetime', fake_datetime):
            request = Request({})
            self.assertEqual(self._callFUT(request), fake_datetime.now())

    def test_with_altair_now(self):
        from datetime import datetime
        from webob.request import Request
        class fake_datetime(datetime):
            @classmethod
            def now(self):
                return 'NOW'

        with mock.patch('altair.httpsession.api.datetime.datetime', fake_datetime):
            request = Request({})
            request.current_time = fake_datetime(2013, 2, 1, 0, 0, 0)
            self.assertEqual(self._callFUT(request), request.current_time)


class HTTPSessionTest(TestCase):
    def _getTarget(self):
        from ..api import HTTPSession
        return HTTPSession

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_id(self):
        dummy_context = mock.MagicMock()
        dummy_context.generate_id.return_value = 'AAAA'
        target = self._makeOne(dummy_context)
        self.assertEqual(target.id, dummy_context.generate_id.return_value)

    def test_load(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = {'XXX': 'THIS IS A TEST'}
        target = self._makeOne(dummy_context)
        self.assertEqual(target.dirty, False)
        self.assertEqual(target._data, None)
        self.assertEqual(target.is_new, True)
        target._id = 'AAAA'
        target.load()
        dummy_context.persistence_backend.load.assert_called_with('AAAA')
        self.assertEqual(target.dirty, False)
        self.assertEqual(target.is_new, False)
        self.assertEqual(target._data, {'XXX': 'THIS IS A TEST'})

    def test_load_in_constructor(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = {'XXX': 'THIS IS A TEST'}
        target = self._makeOne(dummy_context, 'AAAA')
        dummy_context.persistence_backend.load.assert_called_with('AAAA')
        self.assertEqual(target.dirty, False)
        self.assertEqual(target.is_new, False)
        self.assertEqual(target._data, {'XXX': 'THIS IS A TEST'})

    def test_load_in_constructor_error(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.side_effect = Exception()
        target = self._makeOne(dummy_context, 'AAAA')
        dummy_context.persistence_backend.load.assert_called_with('AAAA')
        self.assertEqual(target.dirty, False)
        self.assertEqual(target.is_new, True)
        self.assertEqual(target._id, None)
        self.assertEqual(target._data, None)

    def test_refresh(self):
        dummy_context = mock.MagicMock()
        target = self._makeOne(dummy_context)
        self.assertEqual(target.dirty, False)
        self.assertEqual(target._data, None)
        self.assertEqual(target.is_new, True)
        target._id = 'AAAA'
        target._data = {'YYY': 'JUST AN OLD DATUM'}
        target.dirty = True
        target.refresh()
        dummy_context.persistence_backend.delete.assert_called_with(target._id, target._data)
        dummy_context.persistence_backend.save.assert_called_with(target._id, target._data, False)
        dummy_context.on_delete.assert_called_with(target._id, target._data)
        dummy_context.on_save.assert_called_with(target._id, target._data)
        self.assertEqual(target.dirty, False)
        self.assertEqual(target.is_new, False)
        self.assertEqual(target._data, {'YYY': 'JUST AN OLD DATUM'})

    def test_invalidate_not_dirty(self):
        dummy_context = mock.MagicMock()
        dummy_context.generate_id.return_value = 'BBBB'
        dummy_context.persistence_backend.new.return_value = { 'NEW': 'NEW' }
        target = self._makeOne(dummy_context)
        self.assertEqual(target.dirty, False)
        self.assertEqual(target._data, None)
        target.invalidate()
        dummy_context.persistence_backend.delete.assert_not_called()
        dummy_context.persistence_backend.new.assert_called_with('BBBB')
        dummy_context.on_save.assert_not_called()
        dummy_context.on_new.assert_called_with('BBBB', { 'NEW': 'NEW' })
        self.assertEqual(target.dirty, False)
        self.assertEqual(target.id, 'BBBB')
        self.assertEqual(target._data, { 'NEW': 'NEW' })

    def test_invalidate_dirty(self):
        dummy_context = mock.MagicMock()
        dummy_context.generate_id.return_value = 'BBBB'
        dummy_context.persistence_backend.new.return_value = { 'NEW': 'NEW' }
        target = self._makeOne(dummy_context)
        self.assertEqual(target.dirty, False)
        self.assertEqual(target._data, None)
        target._id = 'AAAA'
        target._data = {'YYY': 'JUST AN OLD DATUM'}
        target.dirty = True
        target.save()
        dummy_context.persistence_backend.save.assert_called_with('AAAA', {'YYY': 'JUST AN OLD DATUM'}, False)
        dummy_context.on_save.assert_called_with('AAAA', {'YYY': 'JUST AN OLD DATUM'})
        target.invalidate()
        dummy_context.persistence_backend.delete.assert_called_with('AAAA', {'YYY': 'JUST AN OLD DATUM'})
        dummy_context.on_delete.assert_called_with('AAAA', {'YYY': 'JUST AN OLD DATUM'})
        dummy_context.persistence_backend.new.assert_called_with('BBBB')
        dummy_context.on_new.assert_called_with('BBBB', { 'NEW': 'NEW' })
        self.assertEqual(target.dirty, False)
        self.assertEqual(target.id, 'BBBB')
        self.assertEqual(target._data, { 'NEW': 'NEW' })

    def test_revert(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = {'XXX': 'THIS IS A TEST'}
        target = self._makeOne(dummy_context, 'AAAA')
        self.assertEqual(target.dirty, False)
        dummy_context.persistence_backend.load.assert_called_with('AAAA')
        self.assertEqual(target._data, {'XXX': 'THIS IS A TEST'})
        target['XXX'] = 'XXX'
        target['YYY'] = 'YYY'
        self.assertTrue(target.dirty)
        self.assertEqual(target._data, {'XXX': 'XXX', 'YYY': 'YYY'})
        target.revert()
        self.assertEqual(target._data, {'XXX': 'THIS IS A TEST'})

    def test_setitem_dirty(self):
        dummy_context = mock.MagicMock()
        target = self._makeOne(dummy_context)
        self.assertEqual(target.dirty, False)
        target['XXXX'] = 'abc'
        self.assertEqual(target.dirty, True)

    def test_pop_dirty(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = { 'YYY': 'abc' }
        target = self._makeOne(dummy_context, '')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)
        self.assertEqual(target.pop('YYY'), 'abc')
        self.assertEqual(target.dirty, True)
        self.assertEqual(len(target), 0)

    def test_pop_dirty2(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = { 'YYY': 'abc' }
        target = self._makeOne(dummy_context, '')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)
        self.assertEqual(target.pop('ZZZ', 'NONEXISTENT'), 'NONEXISTENT')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)

    def test_popitem_dirty(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = { 'YYY': 'abc' }
        target = self._makeOne(dummy_context, '')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)
        self.assertEqual(target.popitem(), ('YYY', 'abc'))
        self.assertEqual(target.dirty, True)
        self.assertEqual(len(target), 0)

    def test_delitem_dirty(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = { 'YYY': 'abc' }
        target = self._makeOne(dummy_context, '')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)
        del target['YYY']
        self.assertEqual(target.dirty, True)
        self.assertEqual(len(target), 0)

    def test_delitem_dirty2(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = { 'YYY': 'abc' }
        target = self._makeOne(dummy_context, '')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)
        with self.assertRaises(KeyError):
            del target['ZZZ']
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)

    def test_setdefault_dirty(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = { 'YYY': 'abc' }
        target = self._makeOne(dummy_context, '')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)
        self.assertEqual(target.setdefault('YYY', 'def'), 'abc')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)

    def test_setdefault_dirty2(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = { 'YYY': 'abc' }
        target = self._makeOne(dummy_context, '')
        self.assertEqual(target.dirty, False)
        self.assertEqual(len(target), 1)
        self.assertEqual(target.setdefault('ZZZ', 'def'), 'def')
        self.assertEqual(target.dirty, True)
        self.assertEqual(len(target), 2)

    def test_created(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = {'XXX': 'THIS IS A TEST'}
        dummy_context.persistence_backend.get_creation_time.return_value = 1
        target = self._makeOne(dummy_context, 'AAAA')
        self.assertEqual(target.created, 1)

    def test_accessed(self):
        dummy_context = mock.MagicMock()
        dummy_context.persistence_backend.load.return_value = {'XXX': 'THIS IS A TEST'}
        dummy_context.persistence_backend.get_access_time.return_value = 2
        target = self._makeOne(dummy_context, 'AAAA')
        self.assertEqual(target.accessed, 2)


class HTTPSessionContextTest(TestCase):
    def _getTarget(self):
        from ..api import HTTPSessionContext
        return HTTPSessionContext

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_on_load(self):
        persistence_backend = mock.Mock()
        http_backend = mock.Mock()
        id_generator = mock.Mock()
        target = self._makeOne(persistence_backend, http_backend, id_generator)
        target.on_load('ID', {'DATA': 'DATA'})
        http_backend.bind.assert_called_with('ID')

    def test_on_save(self):
        persistence_backend = mock.Mock()
        http_backend = mock.Mock()
        id_generator = mock.Mock()
        target = self._makeOne(persistence_backend, http_backend, id_generator)
        target.on_save('ID', {'DATA': 'DATA'})
        http_backend.bind.assert_not_called()
        http_backend.unbind.assert_not_called()

    def test_on_delete(self):
        persistence_backend = mock.Mock()
        http_backend = mock.Mock()
        id_generator = mock.Mock()
        target = self._makeOne(persistence_backend, http_backend, id_generator)
        target.on_delete('ID', {'DATA': 'DATA'})
        http_backend.unbind.assert_called_with('ID')

    def test_generate_id(self):
        persistence_backend = mock.Mock()
        http_backend = mock.Mock()
        id_generator = mock.Mock()
        target = self._makeOne(persistence_backend, http_backend, id_generator)
        target.generate_id()
        id_generator.assert_called()


class DummyCookie(object):
    def __init__(self):
        self.values = {}
        self.params = {}

    def __getitem__(self, key):
        return self.params.setdefault(key, {})

    def __setitem__(self, key, value):
        self.values[key] = value
        if key not in self.params:
            class MyDict(dict):
                def output(self, *args, **kwargs):
                    return 'cookie_out'
            self.params[key] = MyDict()


class CookieSessionBinderTest(TestCase):
    def _getTarget(self):
        from ..api import CookieSessionBinder
        return CookieSessionBinder

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test__set_cookie(self):
        from datetime import datetime

        request = {}
        dummy_cookie = DummyCookie()
        target = self._makeOne(
            cookie=dummy_cookie,
            key='key',
            request=request,
            cookie_domain='test.example.com',
            cookie_path='/path/',
            secure=True,
            httponly=True,
            beaker_compatible=True
            )
        target._set_cookie('ID', datetime(1970, 1, 1, 0, 0, 0))
        self.assertEqual(dummy_cookie.values['key'], 'ID')
        self.assertEqual(dummy_cookie.params['key']['expires'], 'Thu, 01-Jan-1970 00:00:00 GMT')
        self.assertEqual(dummy_cookie.params['key']['domain'], 'test.example.com')
        self.assertEqual(dummy_cookie.params['key']['secure'], True)
        self.assertEqual(dummy_cookie.params['key']['path'], '/path/')
        self.assertEqual(dummy_cookie.params['key']['httponly'], True) 
        self.assertEqual(request['set_cookie'], True)
        self.assertEqual(request['cookie_out'], 'cookie_out')

    def test_bind(self):
        from datetime import datetime, timedelta

        target_class = self._getTarget()

        with mock.patch.object(target_class, '_set_cookie') as set_cookie_mock:
            target = target_class(
                cookie=DummyCookie(),
                key='key',
                cookie_expires=False
                )
            target.bind('ID')
            set_cookie_mock.assert_called_with('ID', datetime(2038, 1, 19, 3, 14, 7))

        with mock.patch.object(target_class, '_set_cookie') as set_cookie_mock:
            target = target_class(
                cookie=DummyCookie(),
                key='key',
                cookie_expires=timedelta(1),
                now=datetime(2013, 1, 1, 0, 0, 0)
                )
            target.bind('ID')
            set_cookie_mock.assert_called_with('ID', target.now + timedelta(1))

        with mock.patch.object(target_class, '_set_cookie') as set_cookie_mock:
            target = target_class(
                cookie=DummyCookie(),
                key='key',
                cookie_expires=datetime(1970, 1, 1, 0, 0, 0)
                )
            target.bind('ID')
            set_cookie_mock.assert_called_with('ID', datetime(1970, 1, 1, 0, 0, 0))


