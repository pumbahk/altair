import logging
import transaction
import json
import pika
from pyramid.threadlocal import get_current_request
from pika.adapters.tornado_connection import TornadoConnection
from zope.interface import implementer, provider
from .interfaces import (
    IConsumer, 
    IPublisherConsumerFactory,
    IMessage,
)

logger = logging.getLogger(__name__)

@implementer(IMessage)
class Message(object):
    def __init__(self, request, channel, method, header, body):
        self.request = request
        self.channel = channel
        self.method = method
        self.header = header
        self.body = body
        self.matchdict = {}

    @property
    def params(self):
        return json.loads(self.body)


@provider(IPublisherConsumerFactory)
def pika_client_factory(config, config_prefix):
    url = config.registry.settings['%s.url' % config_prefix]
    parameters = pika.URLParameters(url)
    return PikaClient(parameters)

class TaskMapper(object):
    Message = Message
    def __init__(self, name, task=None, queue_settings=None, root_factory=None):
        self.task = task
        self.name = name
        self.queue_settings = queue_settings
        self.channel = None
        self.root_factory = root_factory
        logger.debug(self.root_factory)

    def declare_queue(self, channel):
        logger.debug("{name} declare queue {settings}".format(name=self.name,
                                                              settings=self.queue_settings))
        
        channel.queue_declare(queue=self.queue_settings.queue, 
                              durable=self.queue_settings.durable, 
                              exclusive=self.queue_settings.exclusive,
                              auto_delete=self.queue_settings.auto_delete,
                              nowait=self.queue_settings.nowait,
                              callback=self.on_queue_declared)
        self.channel = channel

    def on_queue_declared(self, frame):
        logger.debug('declared: {0}'.format(self.name))
        consumer_tag = self.channel.basic_consume(self.handle_delivery,
                                                  queue=self.queue_settings.queue)
        logger.debug('consume: {0}'.format(consumer_tag))

    def handle_delivery(self, channel, method, header, body):
        try:
            logger.debug('handle delivery: {0}'.format(self.name))
            request = get_current_request()
            message = self.Message(request, channel, method, header, body)
            context = self.root_factory(message)
            logger.debug('call task')
            self.task(context, message)
            transaction.commit()
            channel.basic_ack(method.delivery_tag)
        except Exception as e:
            transaction.abort()
            logger.exception(e)



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
