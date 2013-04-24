# This package may contain traces of nuts
import pika
from . import consumer
from .interfaces import IConsumerFactory, ITask, IConsumer


class QueueSettings(object):
    def __init__(self,
                 queue='',
                 passive=False,
                 durable=False,
                 exclusive=False,
                 auto_delete=False,
                 nowait=False,
                 arguments=None):

        self.queue = queue
        self.passive = passive
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.nowait = nowait
        self.arguments = arguments


def add_task(config, task,
             root_factory=None,
             queue="test",
             durable=True, 
             exclusive=False, 
             auto_delete=False):
    if root_factory is None:
        root_factory = 'pyramid.traversal.DefaultRootFactory'
    reg = config.registry
    root_factory = config.maybe_dotted(root_factory)

    def register():
        pika_consumer = get_consumer(config)
        pika_consumer.add_task(consumer.TaskMapper(task,
                                                   root_factory=root_factory))
        reg.registerUtility(task, ITask)

    config.action("altair.mq.task",
                  register)


def get_consumer(config):
    reg = config.registry
    consumer = reg.queryUtility(IConsumer)

    if consumer is None:
        factory = reg.queryUtility(IConsumerFactory)
        consumer = factory()
        reg.registerUtility(consumer, IConsumer)

    return consumer



        
def includeme(config):
    url = config.registry.settings['altair.mq.url']
    parameters = pika.URLParameters(url)

    config.registry.registerUtility(consumer.PikaClientFactory(parameters))


    config.add_directive("add_task", add_task)
