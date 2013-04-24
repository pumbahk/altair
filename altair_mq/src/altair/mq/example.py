import logging
from pyramid.config import Configurator

from .decorators import task_config
logger = logging.getLogger(__name__)


def main(global_conf, **settings):
    config = Configurator(settings=settings)
    return config.make_wsgi_app()

def includeme(config):
    config.scan(".example")

@task_config()
def sample_task(message):
    from tornado.httpclient import AsyncHTTPClient, HTTPRequest
    logger.debug('got message {body}'.format(body=message.body))
    client = AsyncHTTPClient()
    request = HTTPRequest('http://localhost:8000?value=' + message.body,
                          request_timeout=100)
    client.fetch(request,
                 lambda response: logger.debug('got: {data}'.format(data=response.body)))

    message.channel.basic_ack(message.method.delivery_tag)


@task_config()
def sample_task2(message):
    logger.debug('got message {body}'.format(body=message.body))
    message.channel.basic_ack(message.message.delivery_tag)

