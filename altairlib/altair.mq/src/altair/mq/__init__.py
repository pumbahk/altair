import logging
import urllib
import json
import six
from pyramid.config import ConfigurationError
from .interfaces import IPublisherConsumerFactory, ITask, IConsumer, IPublisher, ITaskDiscovery, ITaskDispatcher

logger = logging.getLogger(__name__)


class QueueSettings(object):
    def __init__(self,
                 queue='',
                 passive=False,
                 durable=True,
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

    def queue_declare(self, task_mapper, channel, callback):
        logger.info("task[{name}]: declaring queue {queue} ({settings})".format(name=task_mapper.name, queue=self.queue, settings=repr(self)))
        def _(frame):
            logger.info("task[{name}] queue {queue} declared".format(name=task_mapper.name, queue=self.queue))
            callback(frame, self.queue)
            
        channel.queue_declare(
            queue=self.queue, 
            passive=self.passive,
            durable=self.durable, 
            exclusive=self.exclusive,
            auto_delete=self.auto_delete,
            nowait=self.nowait,
            arguments=self.arguments,
            callback=_
            )

    @property
    def script_name(self):
        return self.queue

    @property
    def exchange_and_direct_routing_key(self):
        return ('', self.queue)

    def __repr__(self):
        return ("queue={0.queue}, "
                "passive={0.passive}, "
                "durable={0.durable}, "
                "exclusive={0.exclusive}, "
                "auto_delete={0.auto_delete}, "
                "nowait={0.nowait}, "
                "arguments={0.arguments}").format(self)


prefetch_size_setting_name = '%s.qos.prefetch_size' % __name__
prefetch_count_setting_name = '%s.qos.prefetch_count' % __name__

def add_task(config, task,
             name,
             root_factory=None,
             timeout=None,
             consumer="",
             queue=None,
             prefetch_size=None,
             prefetch_count=None,
             **queue_params):
    from .consumer import TaskMapper
    if queue is None:
        queue = name
    elif name == "":
        if isinstance(queue, basestring):
            logger.warning("specifying empty string to `name' parameter with non-empty `queue' parameter is deprecated.  the name of the task will be the same as the queue name (%s)" % queue)
            name = queue
        else:
            raise ConfigurationError("`name' parameter is empty and non-string was specified to `queue' (%r)" % queue)
    if callable(queue):
        queue_settings_factory = queue
    else:
        queue_settings_factory = lambda **rest_of_queue_params: QueueSettings(queue=queue, **rest_of_queue_params)

    if root_factory is not None:
        root_factory = config.maybe_dotted(root_factory)
        logger.info("{name} root factory = {0}".format(root_factory, name=name))
    else:
        logger.info("{name} use default root factory".format(name=name))

    reg = config.registry

    def register():
        pika_consumer = get_consumer(config.registry, consumer)
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

        queue_settings = queue_settings_factory(**queue_params)

        task_mapper = TaskMapper(
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

        pika_consumer.add_task(task_mapper)
        logger.info("register task {name} {root_factory} {queue_settings} {timeout}".format(name=name,
                                                                   root_factory=root_factory,
                                                                   queue_settings=queue_settings,
                                                                   timeout=timeout))
        reg.registerUtility(task, ITask, name='%s:%s' %(consumer, name))

    config.action("altair.mq.task-{name}-{queue}".format(name=name, queue=queue_settings_factory),
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

def dispatch_task(request_or_registry, task_name, body={}, content_type='application/x-www-form-urlencoded', consumer_name='', properties=None, mandatory=False, immediate=False):
    consumer = get_consumer(request_or_registry, name=consumer_name)
    if not ITaskDiscovery.providedBy(consumer):
        raise RuntimeError('consumer %s does not implement ITaskDiscovery' % consumer_name)
    publisher = consumer.companion_publisher
    if publisher is None:
        raise RuntimeError('consumer %s does not have a companion publisher' % consumer_name)
    task_mapper = consumer.lookup_task(task_name)
    exchange, routing_key = task_mapper.queue_settings.exchange_and_direct_routing_key
    if not isinstance(body, basestring):
        if content_type == 'application/x-www-form-urlencoded':
            body = urllib.urlencode([(six.text_type(k).encode('utf-8'), six.text_type(v).encode('utf-8')) for k, v in body.items()])
        elif content_type == 'application/json':
            body = json.dumps(body, ensure_ascii=False)
    if properties is not None:
        properties = dict(properties)
    else:
        properties = {}
    properties['content_type'] = content_type
    publisher.publish(
        exchange=exchange,
        routing_key=routing_key,
        body=body,
        mandatory=mandatory,
        immediate=immediate,
        properties=properties
        )

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
        if ITaskDiscovery.providedBy(consumer):
            config.registry.registerUtility(consumer, ITaskDiscovery, name)
        if publisher is not None:
            consumer.companion_publisher = publisher

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
