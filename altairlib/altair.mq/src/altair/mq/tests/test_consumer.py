import unittest
import mock
from pyramid import testing


class TaskMapperTests(unittest.TestCase):
    def _getTarget(self):
        from ..consumer import TaskMapper
        return TaskMapper

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_declare_queue(self):
        settings = testing.DummyResource(
            queue="",
            durable=True,
            exclusive=False,
            auto_delete=True,
            nowait=False,
        )
        target = self._makeOne("testing", None, settings)
        mock_channel = mock.Mock()
        target.declare_queue(mock_channel)

        mock_channel.queue_declare.assert_called_with(
            queue="",
            callback=target.on_queue_declared,
            durable=True,
            exclusive=False,
            auto_delete=True,
            nowait=False,
        )
        self.assertEqual(target.channel, mock_channel)


    def test_on_queue_declared(self):
        settings = testing.DummyResource(queue="testing")
        target = self._makeOne("testing", None, settings)
        target.channel = mock.Mock()
        mock_frame = mock.Mock()
        target.on_queue_declared(mock_frame)

        target.channel.basic_consume.assert_called_with(target.handle_delivery,
                                                        queue="testing")

    def test_handle_derivery(self):
        settings = testing.DummyResource(queue="testing")
        task = mock.Mock()
        root_factory = mock.Mock()
        target = self._makeOne("testing", task, settings, root_factory)
        channel = mock.Mock()
        method = mock.Mock()
        header = mock.Mock()
        body = mock.Mock()
        target.Message = mock.Mock()
        target.handle_delivery(channel, method, header, body)

        task.assert_called_with(root_factory.return_value,
                                target.Message.return_value)
        target.Message.assert_called_with(channel,
                                          method,
                                          header,
                                          body)


class PikaClientFactoryTests(unittest.TestCase):
    def _getTarget(self):
        from ..consumer import PikaClientFactory
        return PikaClientFactory

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        parameters = mock.Mock()
        target = self._makeOne(parameters)
        result = target()

        self.assertEqual(result.parameters, parameters)


class PikaClientTests(unittest.TestCase):
    
    def _getTarget(self):
        from ..consumer import PikaClient
        return PikaClient

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_connect(self):
        parameters = mock.Mock()
        target = self._makeOne(parameters)
        target.Connection = mock.Mock()

        target.connect()

        target.Connection.assert_called_with(parameters,
                                             target.on_connected)

    def test_on_connected(self):
        
        parameters = mock.Mock()
        target = self._makeOne(parameters)
        connection = mock.Mock()
        
        target.on_connected(connection)

        connection.channel.assert_called_with(target.on_open)

    def test_on_open_with_empty_tasks(self):
        parameters = mock.Mock()
        target = self._makeOne(parameters)
        channel = mock.Mock()

        target.on_open(channel)

    def test_on_open_with_tasks(self):
        parameters = mock.Mock()
        target = self._makeOne(parameters)
        target.tasks.append(mock.Mock())
        channel = mock.Mock()

        target.on_open(channel)

class MessageTests(unittest.TestCase):
    def _getTarget(self):
        from ..consumer import Message
        return Message

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        request = testing.DummyRequest()
        target = self._makeOne(request,
                               channel="testing-channel",
                               method="testing-method",
                               header=["testing-header"],
                               body='"testing-body"')

        self.assertEqual(target.channel, "testing-channel")
        self.assertEqual(target.method, "testing-method")
        self.assertEqual(target.header, ["testing-header"])
        self.assertEqual(target.body, '"testing-body"')

    def test_params(self):
        request = testing.DummyRequest()
        target = self._makeOne(request,
                               channel="testing-channel",
                               method="testing-method",
                               header=["testing-header"],
                               body='{"value": "testing-body"}')
        result = target.params


        self.assertEqual(result, {"value": "testing-body"})
