import logging
import json
from pika.adapters.tornado_connection import TornadoConnection
from zope.interface import implementer
from .interfaces import (
    IConsumer, 
    IConsumerFactory,
    IMessage,
)

logger = logging.getLogger(__name__)

@implementer(IMessage)
class Message(object):
    def __init__(self, channel, method, header, body):
        self.channel = channel
        self.method = method
        self.header = header
        self.body = body

    @property
    def params(self):
        return json.loads(self.body)


@implementer(IConsumerFactory)
class PikaClientFactory(object):
    def __init__(self, parameters):
        self.parameters = parameters

    def __call__(self):
        return PikaClient(self.parameters)

class TaskMapper(object):
    Message = Message
    def __init__(self, name, task=None, queue_settings=None, root_factory=None):
        self.task = task
        self.name = name
        self.queue_settings = queue_settings
        self.channel = None
        self.root_factory = root_factory

    def declare_queue(self, channel):
        logger.debug("{name} declare queue {settings}".format(name=self.name,
                                                              settings=self.queue_settings))
        
        channel.queue_declare(queue=self.queue_settings.queue, 
                              durable=self.queue_settings.durable, 
                              exclusive=self.queue_settings.exclusive,
                              auto_delete=self.queue_settings.auto_delete,
                              callback=self.on_queue_declared)
        self.channel = channel

    def on_queue_declared(self, frame):
        logger.debug('declared')
        self.channel.basic_consume(self.handle_delivery, 
                                   queue=self.queue_settings.queue)

    def handle_delivery(self, channel, method, header, body):
        message = self.Message(channel, method, header, body)
        context = self.root_factory(message)
        self.task(context, message)


@implementer(IConsumer)
class PikaClient(object):
    Connection = TornadoConnection
    def __init__(self, parameters):
        self.parameters = parameters
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def connect(self):
        if not self.tasks:
            logger.warning("no tasks registered")

        logger.info("connecting")
        self.connection = self.Connection(self.parameters,
                                          self.on_connected)

    def on_connected(self, connection):
        logger.debug('connected')
        connection.channel(self.on_open)

    def on_open(self, channel):
        logger.debug('opened')

        for task in self.tasks:
            task.declare_queue(channel)
