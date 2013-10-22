import unittest
import mock
from pyramid import testing

class LocallyDispatchingPublisherConsumerTest(unittest.TestCase):
    def _getTarget(self):
        from ..publisher import LocallyDispatchingPublisherConsumer
        return LocallyDispatchingPublisherConsumer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        from ..interfaces import IConsumer, IPublisher
        config = testing.setUp()
        self.target = self._makeOne()
        config.registry.registerUtility(self.target, IConsumer)
        config.registry.registerUtility(self.target, IPublisher)
        self.config = config

    def tearDown(self):
        testing.tearDown()

    def test_basic(self):
        from altair.mq import add_task
        from altair.mq.consumer import IMessage
        task_called = [0]
        def task_fn(context, message):
            self.assertEqual(context, 'context')
            self.assertTrue(IMessage.providedBy(message))
            self.assertEqual(message.method.routing_key, "route_key")
            self.assertEqual(message.body, "test body")
            task_called[0] += 1
        root_factory = mock.Mock(return_value='context')
        add_task(self.config, task=task_fn, name='', queue="test", root_factory=root_factory)
        self.target.add_route("route_key", "test")
        self.target.publish(routing_key="route_key", body="test body")
        root_factory.assert_called_once()
        self.assertEqual(task_called[0], 1)

    def test_multiple_tasks(self):
        from altair.mq import add_task
        from altair.mq.consumer import IMessage
        task_called = [0]
        def task_fn(context, message):
            self.assertEqual(context, 'context')
            self.assertTrue(IMessage.providedBy(message))
            self.assertEqual(message.method.routing_key, "route_key")
            self.assertEqual(message.body, "test body")
            task_called[0] += 1
        root_factory = mock.Mock(return_value='context')
        add_task(self.config, task=task_fn, name='', queue="test", root_factory=root_factory)
        add_task(self.config, task=task_fn, name='', queue="test", root_factory=root_factory)
        self.target.add_route("route_key", "test")
        self.target.publish(routing_key="route_key", body="test body")
        root_factory.assert_called_once()
        self.assertEqual(task_called[0], 2)

    def test_routing(self):
        from altair.mq import add_task
        from altair.mq.consumer import IMessage
        task_called = {
            'task_fn_1': 0,
            'task_fn_2': 0,
            }
        def task_fn_1(context, message):
            self.assertEqual(context, 'context')
            self.assertTrue(IMessage.providedBy(message))
            self.assertEqual(message.method.routing_key, message.body)
            task_called['task_fn_1'] += 1
            raise Exception
        def task_fn_2(context, message):
            self.assertEqual(context, 'context')
            self.assertTrue(IMessage.providedBy(message))
            self.assertEqual(message.method.routing_key, message.body)
            task_called['task_fn_2'] += 1
        root_factory = mock.Mock(return_value='context')
        add_task(self.config, task=task_fn_1, name='', queue="test1", root_factory=root_factory)
        add_task(self.config, task=task_fn_2, name='', queue="test2", root_factory=root_factory)
        self.target.add_route("route1", "test1")
        self.target.add_route("route2", "test2")
        self.target.add_route("a.*", "test1")
        self.target.add_route("b.*", "test2")
        self.target.add_route("c.#", "test1")

        self.target.publish(routing_key="", body="")
        self.assertEqual(task_called['task_fn_1'], 0)
        self.assertEqual(task_called['task_fn_2'], 0)

        self.target.publish(routing_key="route1", body="route1")
        self.assertEqual(task_called['task_fn_1'], 1)
        self.assertEqual(task_called['task_fn_2'], 0)

        self.target.publish(routing_key="route2", body="route2")
        self.assertEqual(task_called['task_fn_1'], 1)
        self.assertEqual(task_called['task_fn_2'], 1)

        self.target.publish(routing_key="a.test", body="a.test")
        self.assertEqual(task_called['task_fn_1'], 2)
        self.assertEqual(task_called['task_fn_2'], 1)

        self.target.publish(routing_key="b.test", body="b.test")
        self.assertEqual(task_called['task_fn_1'], 2)
        self.assertEqual(task_called['task_fn_2'], 2)

        self.target.publish(routing_key="a.test.test", body="a.test.test")
        self.assertEqual(task_called['task_fn_1'], 2)
        self.assertEqual(task_called['task_fn_2'], 2)

        self.target.publish(routing_key="b.test.test", body="b.test.test")
        self.assertEqual(task_called['task_fn_1'], 2)
        self.assertEqual(task_called['task_fn_2'], 2)

        self.target.publish(routing_key="c.test.test", body="c.test.test")
        self.assertEqual(task_called['task_fn_1'], 3)
        self.assertEqual(task_called['task_fn_2'], 2)
