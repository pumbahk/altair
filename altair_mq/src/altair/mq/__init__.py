# This package may contain traces of nuts
import logging
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from pika.adapters.tornado_connection import TornadoConnection


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PikaClient(object):
    def __init__(self, app, parameters):
        self.parameters = parameters
        self.app = app

    def connect(self):
        logger.debug("connecting")
        self.connection = TornadoConnection(self.parameters,
                                            self.on_connected)

    def on_connected(self, connection):
        logger.debug('connected')
        connection.channel(self.on_open)

    def on_open(self, channel):
        logger.debug('opened')
        self.channel = channel
        channel.queue_declare(queue="test", durable=True, exclusive=False, auto_delete=False, 
                              callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        logger.debug('declared')
        self.channel.basic_consume(self.handle_delivery, queue="test")

    def handle_delivery(self, channel, method, header, body):
        logger.debug('got message {body}'.format(body=body))
        client = AsyncHTTPClient()
        request = HTTPRequest('http://localhost:8000?value=' + body,
                              request_timeout=100)
        client.fetch(request,
                     self.handle_request)
        channel.basic_ack(method.delivery_tag)

    def handle_request(self, response):
        logger.debug('got: {data}'.format(data=response.body))
