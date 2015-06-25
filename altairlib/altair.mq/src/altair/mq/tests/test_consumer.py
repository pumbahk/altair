import unittest
import mock
from pyramid import testing


class TaskMapperTests(unittest.TestCase):
    def _getTarget(self):
        from ..consumer import TaskMapper
        return TaskMapper

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()

    def test_declare_queue(self):
        from .. import QueueSettings
        settings = QueueSettings(
            queue="testing",
            durable=True,
            exclusive=False,
            auto_delete=True,
            nowait=False,
            )
        target = self._makeOne(self.config.registry, "testing", None, settings)
        mock_channel = mock.Mock()
        target.declare_queue(mock_channel)
        self.assertTrue(mock_channel.queue_declare.called)
        self.assertEqual(mock_channel.queue_declare.call_args[1]['queue'], "testing")
        self.assertEqual(mock_channel.queue_declare.call_args[1]['durable'], True)
        self.assertEqual(mock_channel.queue_declare.call_args[1]['exclusive'], False)
        self.assertEqual(mock_channel.queue_declare.call_args[1]['auto_delete'], True)
        self.assertEqual(mock_channel.queue_declare.call_args[1]['nowait'], False)
        callback = mock_channel.queue_declare.call_args[1]['callback']
        dummy_frame = mock.Mock()
        callback(dummy_frame)
        mock_channel.basic_consume.assert_called_with(
            target.handle_delivery,
            queue="testing"
            )



    def test_handle_derivery(self):
        settings = testing.DummyResource(queue="testing")
        task = mock.Mock()
        root_factory = mock.Mock()
        dispatcher = mock.Mock()
        target = self._makeOne(
            registry=self.config.registry,
            name="testing",
            task=task,
            queue_settings=settings,
            root_factory=root_factory,
            task_dispatcher=dispatcher
            )
        channel = mock.Mock()
        method = mock.Mock()
        header = mock.Mock()
        body = mock.Mock()
        target.handle_delivery(channel, method, header, body)
        self.assertEqual(
            dispatcher.call_args[0][0:-1],
            (target, channel, method, header, body)
            )

    def test_handle_derivery_timeout(self):
        settings = testing.DummyResource(queue="testing")
        task = mock.Mock()
        root_factory = mock.Mock()
        class Dispatcher(object):
            def __init__(self):
                self.exception = None

            def __call__(self, *args, **kwargs):
                import time
                try:
                    time.sleep(2)
                except Exception as e:
                    self.exception = e
                
        from ..interfaces import ITaskDispatcher
        dispatcher = Dispatcher()
        from ..consumer import WatchdogDispatcher
        target = self._makeOne(
            registry=self.config.registry,
            name="testing",
            task=task,
            queue_settings=settings,
            root_factory=root_factory,
            task_dispatcher=WatchdogDispatcher(self.config.registry, dispatcher),
            timeout=1
            )
        channel = mock.Mock()
        method = mock.Mock()
        header = mock.Mock()
        body = mock.Mock()
        target.handle_delivery(channel, method, header, body)
        from ..watchdog import TimeoutError
        self.assertIsInstance(dispatcher.exception, TimeoutError)



class PikaClientFactoryTests(unittest.TestCase):
    def _getTarget(self):
        from ..consumer import pika_client_factory 
        return pika_client_factory

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @mock.patch('altair.mq.consumer.PikaClient')
    @mock.patch('pika.URLParameters')
    def test_it(self, _URLParameters, _PikaClient):
        config = testing.DummyModel(
            registry=testing.DummyModel(
                settings={
                    'altair.mq.pika.url': 'url'
                    }
                )
            )
        _URLParameters.return_value = 'XXX'
        _PikaClient.return_value = 'YYY'
        result = self._callFUT(config, 'altair.mq.pika')
        _URLParameters.assert_called_with('url')
        _PikaClient.assert_called_with(config.registry, 'XXX')
        self.assertEqual(result, 'YYY')


class PikaClientTests(unittest.TestCase):
    def setUp(self):
        self.registry = mock.Mock()

    def _getTarget(self):
        from ..consumer import PikaClient
        return PikaClient

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_connect(self):
        parameters = mock.Mock()
        target = self._makeOne(self.registry, parameters)
        target.Connection = mock.Mock()

        target.connect()

        target.Connection.assert_called_with(parameters,
                                             target.on_connected)

    def test_on_connected(self):
        
        parameters = mock.Mock()
        target = self._makeOne(self.registry, parameters)
        connection = mock.Mock()
        
        target.on_connected(connection)

        connection.channel.assert_called_with(target.on_open)

    def test_on_open_with_empty_tasks(self):
        parameters = mock.Mock()
        target = self._makeOne(self.registry, parameters)
        channel = mock.Mock()

        target.on_open(channel)

    def test_on_open_with_tasks(self):
        parameters = mock.Mock()
        target = self._makeOne(self.registry, parameters)
        target.tasks['test'] = mock.Mock()
        channel = mock.Mock()

        target.on_open(channel)

