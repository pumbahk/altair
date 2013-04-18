from zope.interface import Interface, Attribute

class IConsumerFactory(Interface):
    parameters = Attribute(u"connection parameter")

    def __call__(self, task):
        """ create consumer for task """


class IConsumer(Interface):

    queue = Attribute(u"queue name")
    durable = Attribute(u"queue name")
    exclusive = Attribute(u"queue name")
    auto_delete = Attribute(u"queue name")

    def connect():
        """ connect and start Continuation-Passing flow"""


class ITask(Interface):
    def __call__(channel, method, header, body):
        """ execute task by receiving message """
