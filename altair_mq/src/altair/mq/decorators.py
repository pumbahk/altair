import venusian
from . import QueueSettings
from . import add_task

class task_config(object):
    venusian = venusian
    def __init__(self,
                 name="",
                 root_factory=None,
                 queue="",
                 passive=False,
                 durable=True, 
                 exclusive=False, 
                 auto_delete=False,
                 nowait=False,
                 arguments=None):
        self.name = name
        self.root_factory = root_factory
        self.queue_settings = QueueSettings(
                 queue=queue,
                 passive=passive, 
                 durable=durable, 
                 exclusive=exclusive, 
                 auto_delete=auto_delete, 
                 nowait=nowait, 
                 arguments=arguments)


    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            config = scanner.config
            add_task(config,
                     ob,
                     root_factory=self.root_factory,
                     name=self.name,
                     queue=self.queue_settings.queue,
                     durable=self.queue_settings.durable,
                     exclusive=self.queue_settings.exclusive,
                     nowait=self.queue_settings.nowait,
                     auto_delete=self.queue_settings.auto_delete)

        self.venusian.attach(wrapped, callback)
        return wrapped

