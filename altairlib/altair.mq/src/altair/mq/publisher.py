import logging
from altair.mq.interfaces import IPublisher, IConsumer, IPublisherConsumerFactory
from zope.interface import implementer, provider
from pyramid.settings import asbool
from pyramid.config import ConfigurationError
import pika, pika.connection

logger = logging.getLogger(__name__)


@implementer(IPublisher)
class Publisher(object):
    def __init__(self, parameters):
        self.parameters = parameters

    def publish(self, exchange="", routing_key="",
                body="", properties={}, mandatory=False,
                immediate=False):
        logger.debug("publish body={body} exchange={exchange} queue={routing_key}".format(body=body,
                                                                                          exchange=exchange,
                                                                                          routing_key=routing_key))
        connection = pika.BlockingConnection(self.parameters)

        try:
            channel = connection.channel()

            channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=body,
                                  mandatory=mandatory,
                                  immediate=immediate,
                                  properties=pika.BasicProperties(**properties))
            logger.debug("published")

        except Exception as e:
            logger.exception(e)
        finally:
            pass
            #connection.close()


@provider(IPublisherConsumerFactory)
def pika_publisher_factory(config, config_prefix):
    parameters = pika.URLParameters(config.registry.settings['%s.url' % config_prefix])
    return Publisher(parameters)


@implementer(IPublisher, IConsumer)
class LocallyDispatchingPublisherConsumer(object):
    class VirtualConnection(object):
        def __init__(self, params):
            self.params = params

    class VirtualChannel(object):
        def __init__(self, connection):
            self.connection = connection
            self.queue = None
            self.passive = None
            self.durable = None
            self.exclusive = None
            self.auto_delete = None
            self.nowait = None
            self.ack_called = False
            self.callback = None
            self.arguments = None
            self.handler = None

        def queue_declare(self, callback, queue='', passive=False, durable=False, exclusive=False, auto_delete=False, nowait=False, arguments=None):
            self.callback = callback
            self.queue = queue
            self.passive = passive
            self.durable = durable
            self.exclusive = exclusive
            self.auto_delete = auto_delete
            self.nowait = nowait
            self.arguments = arguments

        def basic_qos(self, prefetch_size=0, prefetch_count=0, all_channels=False):
            pass

        def basic_consume(self, handler, queue):
            assert self.queue == queue
            self.handler = handler
            return '%s:%s' % (self.__class__.__name__, self.queue)

        def reset(self):
            self.ack_called = False

        def basic_ack(self, tag):
            self.ack_called = True

        def __repr__(self):
            return '<VirtualChannel queue=%r, durable=%r, exclusive=%r, auto_delete=%r, nowait=%r, handler=%r>' % (self.queue, self.durable, self.exclusive, self.auto_delete, self.nowait, self.handler)

    def __init__(self, continue_on_exception=False):
        self.routes = []
        self.tasks = {}
        self.continue_on_exception = continue_on_exception
        self.virtual_conn = self.VirtualConnection(
            pika.connection.ConnectionParameters()
            )

    def _compile_pattern(self, pattern):
        import re
        return re.compile(re.sub(r'[+.$^?(){}[\]]', lambda g: '\\' + g.group(0), pattern).replace('*', '[^.]+').replace('#', '.+') + '$')

    def add_route(self, pattern, queue):
        self.routes.append({
            'pattern': self._compile_pattern(pattern),
            'queue': queue,
        })

    def add_task(self, task_mapper):
        channel = self.VirtualChannel(self.virtual_conn)
        task_mapper.declare_queue(channel)
        self.tasks.setdefault(task_mapper.queue_settings.queue, []).append(channel)
        channel.callback(None)

    def connect(self):
        if not self.tasks:
            logger.warning("no tasks registered")

    def route(self, exchange, routing_key, body, properties, mandatory, immediate):
        import re
        for route in self.routes:
            if re.match(route['pattern'], routing_key):
                tasks = self.tasks.get(route['queue'])
                if tasks is None:
                    logger.warning("no such queue `%s' is defined" % route['queue'])
                    continue
                for task in tasks:
                    try:
                        task.reset()
                        method = pika.spec.Basic.Deliver(
                            consumer_tag='',
                            delivery_tag='',
                            redelivered=False,
                            routing_key=routing_key,
                            exchange=exchange
                            )
                        task.handler(task, method, properties, body)
                        if not task.ack_called:
                            logger.warning("basic_ack was not called for task %r" % task)
                    except Exception as e:
                        logger.exception("error during running the task %r -- %s" % (task, e))
                        if not self.continue_on_exception:
                            raise

    def publish(self, exchange="", routing_key="",
                body="", properties={}, mandatory=False,
                immediate=False):
        logger.debug("publish body={body} exchange={exchange} queue={routing_key}".format(body=body,
                                                                                          exchange=exchange,
                                                                                          routing_key=routing_key))
        self.route(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=pika.BasicProperties(**properties),
            mandatory=mandatory,
            immediate=immediate
            )
        logger.debug("done")

    def modify_task_dispatcher(self, task_dispatcher):
        return task_dispatcher

@provider(IPublisherConsumerFactory)
def locally_dispatching_publisher_consumer_factory(config, config_prefix):
    import re
    continue_on_exception = asbool(config.registry.settings.get('%s.continue_on_exception' % config_prefix))
    publisher_consumer = LocallyDispatchingPublisherConsumer(
        continue_on_exception=continue_on_exception
        )
    pattern_queue_pairs = [c for c in re.split(r'[ \t]*(?:\r|\n|\r\n)[ \t]*', config.registry.settings.get('%s.routes' % config_prefix, '').strip()) if c]
    for pattern_queue_pair in pattern_queue_pairs:
        pattern_queue_pair = re.split(r'\s*:\s*', pattern_queue_pair, 2)
        if len(pattern_queue_pair) < 2:
            raise ConfigurationError('queue name is missing for %s' % pattern_queue_pair[0])
        publisher_consumer.add_route(pattern_queue_pair[0], pattern_queue_pair[1])
    return publisher_consumer
