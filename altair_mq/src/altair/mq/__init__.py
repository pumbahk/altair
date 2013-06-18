# This package may contain traces of nuts
import logging
import pika
from . import consumer
from .interfaces import IConsumerFactory, ITask, IConsumer


logger = logging.getLogger(__name__)


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

    def __repr__(self):
        return ("queue = {0.queue}; "
                "passive = {0.passive}; "
                "durable = {0.durable}; "
                "exclusive = {0.exclusive}; "
                "auto_delete = {0.auto_delete}; "
                "nowait = {0.nowait}; "
                "arguments = {0.arguments}; ").format(self)

def add_task(config, task,
             name,
             root_factory=None,
             queue="test",
             durable=True, 
             exclusive=False, 
             auto_delete=False,
             nowait=False):
    _root_factory = root_factory
    logger.info("{name} root factory = {0}".format(root_factory, name=name))
    if root_factory is None:
        logger.info("use default root factory")
        root_factory = 'pyramid.traversal.DefaultRootFactory'
    reg = config.registry
    root_factory = config.maybe_dotted(root_factory)
    logger.info("{name} root factory = {0}".format(root_factory, name=name))

    def register():
        pika_consumer = get_consumer(config)
        queue_settings = QueueSettings(queue=queue,
                                       durable=durable,
                                       exclusive=exclusive,
                                       auto_delete=auto_delete,
                                       nowait=nowait)
        if pika_consumer is None:
            return

        pika_consumer.add_task(consumer.TaskMapper(task=task,
                                                   name=name,
                                                   root_factory=root_factory,
                                                   queue_settings=queue_settings))
        logger.info("_root_factory = {0}".format(_root_factory))
        logger.info("register task {name} {root_factory} {queue_settings}".format(name=name,
                                                                   root_factory=root_factory,
                                                                   queue_settings=queue_settings))
        reg.registerUtility(task, ITask)

    config.action("altair.mq.task-{name}".format(name=name),
                  register)


def get_consumer(config):
    reg = config.registry
    consumer = reg.queryUtility(IConsumer)

    if consumer is None:
        factory = reg.queryUtility(IConsumerFactory)
        if factory is None:
            return None
        consumer = factory()
        reg.registerUtility(consumer, IConsumer)

    return consumer



        
def includeme(config):
    url = config.registry.settings['altair.mq.url']
    parameters = pika.URLParameters(url)

    config.registry.registerUtility(consumer.PikaClientFactory(parameters))


    config.add_directive("add_task", add_task)
