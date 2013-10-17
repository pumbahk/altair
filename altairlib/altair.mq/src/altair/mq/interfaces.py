from zope.interface import Interface, Attribute

class IPublisherConsumerFactory(Interface):
    def __call__(config, config_prefix):
        pass


class IConsumer(Interface):

    queue = Attribute(u"queue name")
    durable = Attribute(u"queue name")
    exclusive = Attribute(u"queue name")
    auto_delete = Attribute(u"queue name")

    def connect():
        """ connect and start Continuation-Passing flow"""


class ITask(Interface):
    def __call__(context, message):
        """ execute task by receiving message """


class IMessage(Interface):
    request = Attribute(u"pyramid request for registry")
    channel = Attribute(u"channel of message")
    method = Attribute(u"method of message")
    header = Attribute(u"header of message")
    body = Attribute(u"body of message")
    params = Attribute(u"parameters of this message, maybe parsed body.")


class IPublisher(Interface):
    def publish(exchange="", routing_key="",
                body="", properties={}, mandatory=False,
                intermmediate=False):
        """ publish to queue """
