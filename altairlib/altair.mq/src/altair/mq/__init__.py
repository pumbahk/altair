# This package may contain traces of nuts
import logging
from .interfaces import IPublisherConsumerFactory, ITask, IConsumer, IPublisher, ITaskDispatcher
from pyramid.config import ConfigurationError

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


prefetch_size_setting_name = '%s.qos.prefetch_size' % __name__
prefetch_count_setting_name = '%s.qos.prefetch_count' % __name__

def add_task(config, task,
             name,
             root_factory=None,
             timeout=None,
             queue="test",
             consumer="",
             durable=True, 
             exclusive=False, 
             auto_delete=False,
             nowait=False,
             prefetch_size=None,
             prefetch_count=None):
    from .consumer import TaskMapper

    if root_factory is not None:
        root_factory = config.maybe_dotted(root_factory)
        logger.info("{name} root factory = {0}".format(root_factory, name=name))
    else:
        logger.info("{name} use default root factory".format(name=name))

    reg = config.registry

    def register():
        pika_consumer = get_consumer(config.registry, consumer)
        queue_settings = QueueSettings(queue=queue,
                                       durable=durable,
                                       exclusive=exclusive,
                                       auto_delete=auto_delete,
                                       nowait=nowait)
        if pika_consumer is None:
            raise ConfigurationError("no such consumer: %s" % (consumer or "(default)"))

        if prefetch_size is None:
            try:
                _prefetch_size = int(config.registry.settings.get(prefetch_size_setting_name, 0))
            except (ValueError, TypeError):
                raise ConfigurationError(prefetch_size_setting_name)
        else:
            _prefetch_size = prefetch_size

        if prefetch_count is None:
            try:
                _prefetch_count = int(config.registry.settings.get(prefetch_count_setting_name, 1))
            except (ValueError, TypeError):
                raise ConfigurationError(prefetch_count_setting_name)
        else:
            _prefetch_count = prefetch_count

        task_dispatcher = config.registry.queryUtility(ITaskDispatcher)

        task_dispatcher = pika_consumer.modify_task_dispatcher(task_dispatcher)

        pika_consumer.add_task(
            TaskMapper(
                registry=reg,
                task=task,
                name=name,
                root_factory=root_factory,
                queue_settings=queue_settings,
                task_dispatcher=task_dispatcher,
                timeout=timeout,
                prefetch_size=_prefetch_size,
                prefetch_count=_prefetch_count
                )
            )
        logger.info("register task {name} {root_factory} {queue_settings} {timeout}".format(name=name,
                                                                   root_factory=root_factory,
                                                                   queue_settings=queue_settings,
                                                                   timeout=timeout))
        reg.registerUtility(task, ITask, name=name)

    config.action("altair.mq.task-{name}-{queue}".format(name=name, queue=queue),
                  register, order=2)


def get_consumer(request_or_registry, name=''):
    if hasattr(request_or_registry, 'registry'):
        reg = request_or_registry.registry
    else:
        reg = request_or_registry
    return reg.queryUtility(IConsumer, name)

def get_publisher(request_or_registry, name=''):
    if hasattr(request_or_registry, 'registry'):
        reg = request_or_registry.registry
    else:
        reg = request_or_registry
    return reg.queryUtility(IPublisher, name)

def add_publisher_consumer(config, name, config_prefix, dotted_names=None):
    if dotted_names is None:
        import re
        dotted_names = [c for c in re.split(r'(?:\s*,\s*|\s+)', config.registry.settings[config_prefix].strip()) if c]

    publisher = consumer = None

    for dotted_name in dotted_names:
        factory = config.maybe_dotted(dotted_name)
        publisher_or_consumer = factory(config, config_prefix)
        if IPublisher.providedBy(publisher_or_consumer):
            if publisher is not None:
                raise ConfigurationError('publisher is already defined for %s' % name)
            publisher = publisher_or_consumer
        if IConsumer.providedBy(publisher_or_consumer):
            if consumer is not None:
                raise ConfigurationError('consumer is already defined for %s' % name)
            consumer = publisher_or_consumer

    if publisher is not None:
        config.registry.registerUtility(publisher, IPublisher, name)
    if consumer is not None:
        config.registry.registerUtility(consumer, IConsumer, name)


def includeme(config):
    import sys
    from . import consumer, publisher

    def register_task_dispatcher():
        task_dispatcher_factory = config.registry.settings.get('%s.task_dispatcher' % __name__)
        if task_dispatcher_factory is not None:
            task_dispatcher_factory = config.maybe_dotted(task_dispatcher_factory)
        else:
            task_dispatcher_factory = consumer.TaskDispatcher

        task_dispatcher_middlewares = config.registry.settings.get('%s.task_dispatcher_middlewares' % __name__)
        if task_dispatcher_middlewares:
            task_dispatcher_middlewares = [config.maybe_dotted(c) for c in re.split(r'(?:\s*,\s*|\s+)', task_dispatcher_middlewares) if c]
        else:
            task_dispatcher_middlewares = None

        task_dispatcher = task_dispatcher_factory(config.registry) 
        if task_dispatcher_middlewares is not None:
            logger.info('task_dispatcher_middlewares=%r' % task_dispatcher_middlewares)
            for middleware in task_dispatcher_middlewares:
                task_dispatcher = middleware(config.registry, task_dispatcher)
        config.registry.registerUtility(task_dispatcher, ITaskDispatcher)
    # this has to be run after all the tweens are registered
    config.action("altair.mq.register_task_dispatcher", register_task_dispatcher, order=1)

    config.add_directive("add_task", add_task)
    config.add_directive("add_publisher_consumer", add_publisher_consumer)
