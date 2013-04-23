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
        consumer = get_consumer()
        reg.registerUtility(task, ITask)

    config.action("altair.mq.task",
                  register)


def get_consumer(config):
    reg = config.registry
    consumer = reg.queryUtility(IConsumer)

    if consumer is None:
        factory = reg.adapters.lookup([ITask], IConsumerFactory, "")
        consumer = factory()
        reg.adapters.register([ITask], IConsumer, "", 
                              consumer)
    return consumer



        
def includeme(config):
    url = config.registry.settings['altair.mq.url']
    parameters = pika.URLParameters(url)

    config.registry.adapters.register([ITask], IConsumerFactory, "", 
                                      consumer.PikaClientFactory(parameters))


    config.add_directive("add_task", add_task)
