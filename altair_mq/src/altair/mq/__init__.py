# This package may contain traces of nuts
import pika
from . import consumer
from .interfaces import IConsumerFactory, ITask, IConsumer

def add_task(config, task):
    task
    reg = config.registry

    def register():
        factory = reg.adapters.lookup([ITask], IConsumerFactory, "")
        consumer = factory(task)
        reg.registerUtility(consumer)

    config.action("altair.mq.task",
                  register)


def get_consumer(request):
    reg = request.registry
    return reg.queryUtility(IConsumer)

def includeme(config):
    url = config.registry.settings['altair.mq.url']
    parameters = pika.URLParameters(url)

    config.registry.adapters.register([ITask], IConsumerFactory, "", 
                                      consumer.PikaClientFactory(parameters))


    config.add_directive("add_task", add_task)
