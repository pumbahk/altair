import logging
from tornado import gen
from .decorators import task_config
logger = logging.getLogger(__name__)


def includeme(config):
    #config.add_task(sample_task)
    config.scan(".example")

@task_config()
@gen.coroutine
def sample_task(channel, method, header, body):
    from tornado.httpclient import AsyncHTTPClient, HTTPRequest
    logger.debug('got message {body}'.format(body=body))
    client = AsyncHTTPClient()
    request = HTTPRequest('http://localhost:8000?value=' + body,
                          request_timeout=100)
    response = yield client.fetch(request)
    logger.debug('got: {data}'.format(data=response.body))
    channel.basic_ack(method.delivery_tag)


