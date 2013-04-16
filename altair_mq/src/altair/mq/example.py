import logging

logger = logging.getLogger(__name__)


def includeme(config):
    config.add_task(sample_task)

def sample_task(channel, method, header, body):
    from tornado.httpclient import AsyncHTTPClient, HTTPRequest
    logger.debug('got message {body}'.format(body=body))
    client = AsyncHTTPClient()
    request = HTTPRequest('http://localhost:8000?value=' + body,
                          request_timeout=100)
    client.fetch(request,
                 lambda response: logger.debug('got: {data}'.format(data=response.body)))

    channel.basic_ack(method.delivery_tag)


