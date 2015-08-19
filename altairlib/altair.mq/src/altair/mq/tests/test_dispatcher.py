import unittest
import mock
from pyramid.testing import setUp, tearDown
import pika.spec

def dummy_tween_factory(name):
    def _(ingress, registry):
        def _(request):
            if not hasattr(request, 'tweens_called'):
                request.tweens_called = {}
            request.tweens_called[name] = (request, ingress)
            return ingress(request)
        return _
    return _

dummy_tween_1 = dummy_tween_factory('dummy_tween_1')
dummy_tween_2 = dummy_tween_factory('dummy_tween_2')

class TaskDispatcherTest(unittest.TestCase):
    def setUp(self):
        self.config = setUp()

    def tearDown(self):
        tearDown()

    def _getTarget(self):
        from ..consumer import TaskDispatcher
        return TaskDispatcher

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_imessage_iface(self):
        default_root_factory = mock.Mock(return_value='ROOT')
        self.config.set_root_factory(default_root_factory)
        target = self._makeOne(self.config.registry)
        task_mapper = mock.Mock(root_factory=None, queue_settings=mock.Mock(queue='QUEUE', script_name=''))
        channel = mock.Mock()
        method = mock.Mock(method_tag=u'XXX')
        properties = pika.spec.BasicProperties(content_type='application/json')
        body = b'"body"'
        continuation = mock.Mock()
        target(
            task_mapper=task_mapper,
            channel=channel,
            method=method,
            properties=properties,
            body=body,
            continuation=continuation
            )
        self.assertTrue(continuation.called)
        self.assertTrue(task_mapper.task.called)
        context, request = task_mapper.task.call_args[0]
        from ..interfaces import IMessage
        self.assertTrue(IMessage.providedBy(request))
        from zope.interface.verify import verifyObject
        verifyObject(IMessage, request)

    def test_default_root_factory(self):
        default_root_factory = mock.Mock(return_value='ROOT')
        self.config.set_root_factory(default_root_factory)
        target = self._makeOne(self.config.registry)
        task_mapper = mock.Mock(root_factory=None, queue_settings=mock.Mock(queue='QUEUE', script_name=''))
        channel = mock.Mock()
        method = mock.Mock(method_tag=u'XXX')
        properties = pika.spec.BasicProperties(content_type='application/json')
        body = b'"body"'
        continuation = mock.Mock()
        target(
            task_mapper=task_mapper,
            channel=channel,
            method=method,
            properties=properties,
            body=body,
            continuation=continuation
            )
        self.assertTrue(continuation.called)
        self.assertTrue(task_mapper.task.called)
        context, request = task_mapper.task.call_args[0]
        self.assertEqual(default_root_factory.call_args[0], (request, ))
        self.assertEqual('ROOT', context)

    def test_tweens(self):
        self.config.add_tween('%s.dummy_tween_1' % __name__)
        self.config.add_tween('%s.dummy_tween_2' % __name__)
        target = self._makeOne(self.config.registry)
        task_mapper = mock.Mock(queue_settings=mock.Mock(queue='QUEUE', script_name=''))
        channel = mock.Mock()
        method = mock.Mock(method_tag=u'XXX')
        properties = pika.spec.BasicProperties(content_type='application/json')
        body = b'"body"'
        continuation = mock.Mock()
        target(
            task_mapper=task_mapper,
            channel=channel,
            method=method,
            properties=properties,
            body=body,
            continuation=continuation
            )
        self.assertTrue(continuation.called)
        self.assertTrue(task_mapper.task.called)
        context, request = task_mapper.task.call_args[0]
        self.assertEqual(len(request.tweens_called), 2)
        self.assertIn('dummy_tween_1', request.tweens_called)
        self.assertIn('dummy_tween_2', request.tweens_called)

    def test_request_extensions(self):
        req_method = mock.Mock(return_value='AAA')
        self.config.add_request_method(req_method, name='req_method', property=True)
        target = self._makeOne(self.config.registry)
        task_mapper = mock.Mock(queue_settings=mock.Mock(queue='QUEUE', script_name=''))
        channel = mock.Mock()
        method = mock.Mock(method_tag=u'XXX')
        properties = pika.spec.BasicProperties(content_type='application/json')
        body = b'"body"'
        continuation = mock.Mock()
        target(
            task_mapper=task_mapper,
            channel=channel,
            method=method,
            properties=properties,
            body=body,
            continuation=continuation
            )
        self.assertTrue(continuation.called)
        self.assertTrue(task_mapper.task.called)
        context, request = task_mapper.task.call_args[0]
        self.assertTrue(hasattr(request, 'req_method'))
        self.assertEqual('AAA', request.req_method)

