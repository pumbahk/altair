import unittest
from pyramid import testing
import mock

class DummyException(Exception):
    pass

class as_globals_listTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import as_globals_list
        return as_globals_list(*args, **kwargs)

    def test_zero(self):
        value = ""
        result = self._callFUT(value)

        self.assertEqual(result, [])

    def test_builtin(self):
        value = "Exception"
        result = self._callFUT(value)

        self.assertEqual(result, [Exception])

    def test_package(self):
        value = "altair.exclog.tests.DummyException"
        result = self._callFUT(value)

        self.assertEqual(result, [DummyException])


class ExcLogTweenTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from .tweens import ExcLogTween
        return ExcLogTween

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        from pyramid.httpexceptions import WSGIHTTPException

        registry = self.config.registry
        from . import create_exception_message_builder, create_exception_message_renderer, create_exception_logger
        from .interfaces import IExceptionMessageBuilder, IExceptionMessageRenderer, IExceptionLogger
        registry.registerUtility(create_exception_message_builder(registry), IExceptionMessageBuilder)
        registry.registerUtility(create_exception_message_renderer(registry), IExceptionMessageRenderer)
        registry.registerUtility(create_exception_logger(registry), IExceptionLogger)
        handler = testing.DummyResource()
        result = self._makeOne(handler, registry)

        self.assertEqual(result.handler, handler)
        self.assertEqual(result.registry, registry)
        self.assertTrue(result.message_builder.extra_info)
        self.assertEqual(result.ignored, 
                         (WSGIHTTPException,))


    @mock.patch('altair.exclog.logger')
    def test_call_with_exception(self, mock_logger):
        registry = self.config.registry
        registry.settings['altair.exclog.includes'] = 'testing'
        from . import create_exception_message_builder, create_exception_message_renderer, create_exception_logger
        from .interfaces import IExceptionMessageBuilder, IExceptionMessageRenderer, IExceptionLogger
        registry.registerUtility(create_exception_message_builder(registry), IExceptionMessageBuilder)
        registry.registerUtility(create_exception_message_renderer(registry), IExceptionMessageRenderer)
        registry.registerUtility(create_exception_logger(registry), IExceptionLogger)

        handler = mock.Mock()
        handler.side_effect = Exception()

        tween = self._makeOne(handler, registry)

        request = testing.DummyRequest()
        request.environ['testing'] = 'testing'  # test marker
        request.params['testing_param'] = "it's testing"  # test marker

        result = tween(request)

        self.assertEqual(result.status_int, 500)
        self.assertEqual(result.text, u'')
        mock_logger.exception.assert_called_with('\n\nhttp://example.com\n\n'
                                                 'ENVIRONMENT\n\n'
                                                 '{\'testing\': \'testing\'}\n\n'
                                                 '\n\n')

    def test_call_with_handler(self):
        registry = self.config.registry
        handler = mock.Mock()
        request = testing.DummyRequest()
        handler.return_value = request.response

        tween = self._makeOne(handler, registry)


        result = tween(request)

        self.assertEqual(result, request.response)
        self.assertEqual(result.text, u'')

    def test_call_with_ignore(self):

        registry = self.config.registry
        registry.settings['altair.exclog.ignored'] = (DummyException,)

        handler = mock.Mock()
        request = testing.DummyRequest()
        handler.side_effect = DummyException()

        tween = self._makeOne(handler, registry)


        self.assertRaises(DummyException, tween, request)


    @mock.patch('altair.exclog.logger')
    def test_call_with_short_message(self, mock_logger):
        registry = self.config.registry
        from . import create_exception_message_builder, create_exception_message_renderer, create_exception_logger
        from .interfaces import IExceptionMessageBuilder, IExceptionMessageRenderer, IExceptionLogger
        registry.registerUtility(create_exception_message_builder(registry), IExceptionMessageBuilder)
        registry.registerUtility(create_exception_message_renderer(registry), IExceptionMessageRenderer)
        registry.registerUtility(create_exception_logger(registry), IExceptionLogger)

        handler = mock.Mock()
        request = testing.DummyRequest()
        handler.side_effect = DummyException()

        tween = self._makeOne(handler, registry)
        tween.message_builder.extra_info = False
        result = tween(request)

        self.assertEqual(result.status_int, 500)
        mock_logger.exception.assert_called_with('http://example.com')
        self.assertEqual(result.text, u'')

    @mock.patch('altair.exclog.logger')
    def test_call_with_tb_view(self, mock_logger):
        registry = self.config.registry
        from . import create_exception_message_builder, create_exception_message_renderer, create_exception_logger
        from .interfaces import IExceptionMessageBuilder, IExceptionMessageRenderer, IExceptionLogger
        registry.registerUtility(create_exception_message_builder(registry), IExceptionMessageBuilder)
        registry.registerUtility(create_exception_message_renderer(registry), IExceptionMessageRenderer)
        registry.registerUtility(create_exception_logger(registry), IExceptionLogger)

        handler = mock.Mock()
        request = testing.DummyRequest()
        handler.side_effect = DummyException()

        tween = self._makeOne(handler, registry)
        tween.show_traceback = True
        tween.message_builder.extra_info = False
        result = tween(request)

        self.assertEqual(result.status_int, 500)
        mock_logger.exception.assert_called_with('http://example.com')
        self.assertEqual(result.text.split()[0], "http://example.com")
        self.assertIn('Traceback (most recent call last):', result.text)
        self.assertTrue(result.text.split()[-1], "DummyException")


class convert_settingsTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import _convert_settings
        return _convert_settings(*args, **kwargs)


    def test_it(self):
        settings = {"altair.exclog.extra_info": "",
                    "altair.exclog.ignored": "Exception ValueError",
                    "altair.exclog.show_traceback": "true",
        }

        self._callFUT(settings)

        self.assertFalse(settings['altair.exclog.extra_info'])
        self.assertEqual(settings['altair.exclog.ignored'],
                         (Exception, ValueError,))
        self.assertTrue(settings['altair.exclog.show_traceback'])
