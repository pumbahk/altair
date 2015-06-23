from . import QueueSettings

class DelayedQueueSettings(object):
    def __init__(self, queue='', delay_queue=None, delay=None, **queue_params):
        if delay_queue is None:
            delay_queue = '%s-DELAY(%d)' % (queue, delay)
        self.queue_settings = QueueSettings(
            delay_queue,
            **queue_params
            )
        delay_queue_params = dict(queue_params)
        delay_queue_params.update(
            arguments={
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': delay_queue,
                'x-message-ttl': delay,
                }
            )
        self.delay_queue_settings = QueueSettings(
            queue,
            **delay_queue_params
            )

    @property
    def script_name(self):
        return self.delay_queue_settings.queue

    def queue_declare(self, task_mapper, channel, callback):
        def on_queue_declared(frame, _):
            self.queue_settings.queue_declare(task_mapper, channel, callback)
        self.delay_queue_settings.queue_declare(task_mapper, channel, on_queue_declared)


def delayed_queue(queue, delay_queue=None, delay=None):
    def _(**queue_params):
        return DelayedQueueSettings(queue, delay_queue, delay, **queue_params)
    return _
