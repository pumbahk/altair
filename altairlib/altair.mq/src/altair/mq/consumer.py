import logging
import transaction
import json
import pika
from pyramid.config import ConfigurationError
from pyramid.interfaces import IRequestFactory, IRequestExtensions, ITweens, IDefaultRootFactory
from pyramid.request import Request
from pyramid.events import NewRequest, ContextFound
from pyramid.threadlocal import manager
from pika.adapters.tornado_connection import TornadoConnection
from zope.interface import implementer, provider, directlyProvides
from .interfaces import (
    IConsumer, 
    IPublisherConsumerFactory,
    IMessage,
    ITaskDispatcher,
    IWorkers,
)
from .watchdog import Watchdog

logger = logging.getLogger(__name__)

@provider(IPublisherConsumerFactory)
def pika_client_factory(config, config_prefix):
    setting_name = '%s.url' % config_prefix
    url = config.registry.settings.get(setting_name)
    if url is None:
        raise ConfigurationError('missing configuration: %s' % setting_name)
    parameters = pika.URLParameters(url)
    return PikaClient(config.registry, parameters)

class TaskMapper(object):
    def __init__(self, registry, name, task=None, queue_settings=None, root_factory=None, task_dispatcher=None, prefetch_size=0, prefetch_count=1, **kwargs):
        self.registry = registry
        self.name = name
        self.task = task
        self.queue_settings = queue_settings
        self.channel = None
        self.root_factory = root_factory
        self.prefetch_size = prefetch_size
        self.prefetch_count = prefetch_count
        self.task_dispatcher = task_dispatcher
        self.args = kwargs

    def __repr__(self):
        return 'TaskMapper(name=%r, task=%r, queue_settings=%r, root_factory=%r, task_dispatcher=%r, prefetch_size=%r, prefetch_count=%r, **kwargs=%r)' % (
            self.name, self.task, self.queue_settings, self.root_factory, self.task_dispatcher, self.prefetch_size, self.prefetch_count, self.args
            )

    def declare_queue(self, channel):
        logger.debug("{name} declare queue {settings}".format(name=self.name,
                                                              settings=self.queue_settings))

        def on_queue_declared(frame):
            logger.debug('declared: {0}'.format(self.name))
            channel.basic_qos(
                prefetch_size=self.prefetch_size,
                prefetch_count=self.prefetch_count
                )
            consumer_tag = channel.basic_consume(self.handle_delivery,
                                                      queue=self.queue_settings.queue)
            logger.debug('consume: {0}'.format(consumer_tag))
        
        channel.queue_declare(queue=self.queue_settings.queue, 
                              durable=self.queue_settings.durable, 
                              exclusive=self.queue_settings.exclusive,
                              auto_delete=self.queue_settings.auto_delete,
                              nowait=self.queue_settings.nowait,
                              callback=on_queue_declared)

    def handle_delivery(self, channel, method, properties, body):
        logger.debug('handle_delivery: self=%r, channel=%s, method=%s, properties=%r, body=%s' % (self, channel, method, properties, body))
        try:
            self.task_dispatcher(
                self,
                channel,
                method,
                properties,
                body,
                lambda: channel.basic_ack(method.delivery_tag)
                )
        except:
            logger.error('failed to handle message', exc_info=True)

   
class WatchdogDispatcher(object):
    def __init__(self, registry, handler):
        self.registry = registry
        self.handler = handler

    def __call__(self, task_mapper, channel, method, properties, body, continuation):
        with Watchdog(task_mapper.args['timeout']):
            self.handler(task_mapper, channel, method, properties, body, continuation)


class WorkerDispatcher(object):
    def __init__(self, registry, handler):
        self.registry = registry
        self.handler = handler

    def _worker_do(self, f):
        workers = self.registry.getUtility(IWorkers)
        workers.dispatch(f)

    def __call__(self, task_mapper, channel, method, properties, body, continuation):
        self._worker_do(lambda: self.handler(task_mapper, channel, method, properties, body, continuation))


class TaskDispatcher(object):
    threadlocal_manager = manager

    def __init__(self, registry):
        self.request_factory = registry.queryUtility(IRequestFactory, default=Request)
        self.request_extensions = registry.queryUtility(IRequestExtensions)
        tweens = registry.queryUtility(ITweens)
        if tweens is not None:
            self._handle_request = tweens(self._handle_request, registry)
        self.registry = registry
        self.root_factory = registry.queryUtility(IDefaultRootFactory)

    def _handle_request(self, request):
        root_factory = request.task_mapper.root_factory or self.root_factory
        context = root_factory(request)
        request.context = context
        self.registry.has_listeners and self.registry.notify(ContextFound(request))
        request.task_mapper.task(context, request)
        return request.response

    def __call__(self, task_mapper, channel, method, properties, body, continuation):
        conn_params = channel.connection.params
        environ = {
            'REQUEST_METHOD': 'POST',
            'SCRIPT_NAME': '/' + task_mapper.queue_settings.queue,
            'PATH_INFO': task_mapper.name,
            'wsgi.url_scheme': 'amqps' if conn_params.ssl else 'amqp',
            'SERVER_NAME': conn_params.host,
            'SERVER_PORT': conn_params.port,
            }
        if properties is not None:
            environ.update({
                'CONTENT_TYPE': properties.content_type,
                'amqp.delivery_mode': properties.delivery_mode,
                'amqp.priority': properties.priority,
                'amqp.correlation_id': properties.correlation_id,
                'amqp.reply_to': properties.reply_to,
                'amqp.expiration': properties.expiration,
                'amqp.message_id': properties.message_id,
                'amqp.type': properties.type,
                'amqp.user_id': properties.user_id,
                'amqp.app_id': properties.app_id,
                'amqp.cluster_id': properties.cluster_id,
                })
        request = self.request_factory(environ)
        if properties is not None and properties.headers is not None:
            request.headers.update(properties.headers)
        request.task_mapper = task_mapper
        request.pika_channel = channel
        request.pika_method = method
        request.body = body
        if request.content_type == 'application/json':
            request.environ['webob._parsed_post_vars'] = (json.loads(body), request.body_file_raw)
        elif request.content_type == 'application/octet-stream':
            # B/W compatibility
            try:
                request.environ['webob._parsed_post_vars'] = (json.loads(body), request.body_file_raw)
            except:
                logger.warning('failed to parse body as JSON')
           
        directlyProvides(request, IMessage)
        threadlocals = {'registry': self.registry, 'request': request}
        self.threadlocal_manager.push(threadlocals)
        request.registry = self.registry
        try:
            try:
                extensions = self.request_extensions
                if extensions is not None:
                    request._set_extensions(extensions)
                self.registry.has_listeners and self.registry.notify(NewRequest(request))
                self._handle_request(request)
                if continuation is not None:
                    continuation()
            finally:
                 finished_callbacks = getattr(request, 'finished_callbacks', None)
                 if finished_callbacks is not None:
                    process_finished_callbacks = getattr(request, '_process_finished_callbacks', None)
                    if callable(process_finished_callbacks):
                        process_finished_callbacks()
        finally:
            self.threadlocal_manager.pop()


@implementer(IConsumer)
class PikaClient(object):
    Connection = TornadoConnection
    def __init__(self, registry, parameters, reconnection_interval=10):
        self.registry = registry
        self.parameters = parameters
        self.tasks = []
        self.reconnection_interval = reconnection_interval

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
        connection.add_on_close_callback(self.on_close)

    def on_open(self, channel):
        logger.debug('opened')

        for task in self.tasks:
            task.declare_queue(channel)

    def on_close(self, connection, reply_code, reply_text):
        if self.reconnection_interval > 0:
            logger.info('connection has been closed; reconnecting in %d seconds' % self.reconnection_interval)
            self.connection.add_timeout(
                self.reconnection_interval,
                self.connect)

    def modify_task_dispatcher(self, task_dispatcher):
        task_dispatcher = WatchdogDispatcher(self.registry, task_dispatcher)
        task_dispatcher = WorkerDispatcher(self.registry, task_dispatcher)
        return task_dispatcher
