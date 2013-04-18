import logging
from pika.adapters.tornado_connection import TornadoConnection
from zope.interface import implementer
from .interfaces import IConsumer, IConsumerFactory

logger = logging.getLogger(__name__)

@implementer(IConsumerFactory)
class PikaClientFactory(object):

    def __init__(self, parameters):
        self.parameters = parameters

    def __call__(self, task,
                 queue="test",
                 durable=True, 
                 exclusive=False, 
                 auto_delete=False):

        return PikaClient(task, self.parameters,
                          queue=queue,
                          durable=durable, 
                          exclusive=exclusive, 
                          auto_delete=auto_delete)



@implementer(IConsumer)
class PikaClient(object):
    def __init__(self, task, parameters,
                 queue="test",
                 durable=True, 
                 exclusive=False, 
                 auto_delete=False):

        self.task = task
        self.parameters = parameters
        self.queue = queue
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete

    def connect(self):
        logger.info("connecting")
        self.connection = TornadoConnection(self.parameters,
                                            self.on_connected)

    def on_connected(self, connection):
        logger.debug('connected')
        connection.channel(self.on_open)

    def on_open(self, channel):
        logger.debug('opened')
        self.channel = channel
        channel.queue_declare(queue=self.queue, 
                              durable=self.durable, 
                              exclusive=self.exclusive,
                              auto_delete=self.auto_delete, 
                              callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        logger.debug('declared')
        self.channel.basic_consume(self.handle_delivery, queue="test")

    def handle_delivery(self, channel, method, header, body):
        self.task(channel, method, header, body)
    #     logger.debug('got message {body}'.format(body=body))
    #     client = AsyncHTTPClient()
    #     request = HTTPRequest('http://localhost:8000?value=' + body,
    #                           request_timeout=100)
    #     client.fetch(request,
    #                  self.handle_request)
    #     channel.basic_ack(method.delivery_tag)

    # def handle_request(self, response):
    #     logger.debug('got: {data}'.format(data=response.body))
