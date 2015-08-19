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

    def add_task(task_mapper):
        pass


class ITask(Interface):
    def __call__(context, message):
        """ execute task by receiving message """


class IMessage(Interface):
    pika_channel = Attribute(u"channel of message")
    pika_method = Attribute(u"method of message")
    body = Attribute(u"body of message")
    params = Attribute(u"parameters of this message, maybe parsed body.")


class IPublisher(Interface):
    def publish(exchange="", routing_key="",
                body="", properties={}, mandatory=False,
                intermmediate=False):
        """ publish to queue """

class ITaskDispatcher(Interface):
    def __call__(task, channel, method, properties, body):
        pass

class ITaskDiscovery(Interface):
    def add_task(task_mapper):
        pass

    def lookup_task(name):
        pass

class IWorkers(Interface):
    def dispatch(fn):
        pass

class IWorker(Interface):
    def start():
        pass

    def stop(fn):
        pass

    def __call__(fn):
        pass
