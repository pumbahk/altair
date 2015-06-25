import unittest
from pyramid import testing



class TestIt(unittest.TestCase):
    
    settings = {
        'altair.mq': '..publisher.pika_publisher_factory, ..consumer.pika_client_factory',
        'altair.mq.url': 'amqp://guest:guest@localhost:5672/%2F',
    }
    def setUp(self):
        self.config = testing.setUp(settings=self.settings)

    def tearDown(self):
        testing.tearDown()


    def test_it(self):
        from altair.mq.interfaces import IConsumer
        self.config.include('altair.mq')
        self.config.include('altair.mq.example')

        reg = self.config.registry

        consumer = reg.queryUtility(IConsumer)

        self.assertIsNotNone(consumer)
        self.assertTrue(consumer.tasks)
        self.assertEqual(consumer.tasks.popitem()[1].root_factory, None)
