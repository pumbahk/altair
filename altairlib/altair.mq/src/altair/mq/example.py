import logging
from pyramid.config import Configurator

from .decorators import task_config
logger = logging.getLogger(__name__)


def main(global_conf, **settings):
    config = Configurator(settings=settings)
    return config.make_wsgi_app()

def includeme(config):
    config.scan(".example")

@task_config(name="sample1", queue="test", durable=True, exclusive=False, auto_delete=False)
def sample_task(context, message):
    from tornado.httpclient import AsyncHTTPClient, HTTPRequest
    logger.debug('got message {body}'.format(body=message.body))
    client = AsyncHTTPClient()
    request = HTTPRequest('http://localhost:8000?value=' + message.body,
                          request_timeout=100)
    client.fetch(request,
                 lambda response: logger.debug('got: {data}'.format(data=response.body)))

    message.channel.basic_ack(message.method.delivery_tag)


class ExampleResource(object):
    def __init__(self, message):
        self.message = message

    @property
    def value(self):
        return self.message.params.get('value')

@task_config(name="sample2")
def sample_task2(context, message):
    logger.debug('context value = {value}'.format(context.value))
    logger.debug('got message {body}'.format(body=message.body))
    message.channel.basic_ack(message.message.delivery_tag)

