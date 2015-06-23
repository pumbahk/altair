import venusian
from . import add_task

class task_config(object):
    venusian = venusian
    def __init__(self,
                 name="",
                 root_factory=None,
                 timeout=None,
                 consumer="",
                 queue="",
                 **queue_params):
        self.name = name
        self.root_factory = root_factory
        self.timeout = timeout
        self.consumer = consumer
        self.queue = queue
        self.queue_params = queue_params


    def __call__(self, wrapped):
        def callback(scanner, name, ob):
            config = scanner.config
            add_task(config,
                     ob,
                     name=self.name,
                     root_factory=self.root_factory,
                     timeout=self.timeout,
                     queue=self.queue,
                     consumer=self.consumer,
                     **self.queue_params
                     )

        self.venusian.attach(wrapped, callback)
        return wrapped

