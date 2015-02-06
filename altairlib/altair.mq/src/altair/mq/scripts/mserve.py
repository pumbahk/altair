import sys
import logging
import argparse
import threading
import signal
from datetime import timedelta
from Queue import Queue, Empty as EmptyException
from collections import deque
from pyramid.config import global_registries
from zope.interface import implementer

from pyramid.paster import get_app, setup_logging

from tornado import ioloop
from .. import get_consumer
from ..interfaces import IWorker, IWorkers

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    pass


class Nothing(object):
    def __new__(cls):
        return cls


class Future(object):
    def __init__(self):
        self.cv = threading.Condition()
        self.value = None 
        self.value_available = False

    def trygetvalue(self, default=Nothing()):
        self.cv.acquire()
        try:
            if not self.value_available:
                if default is Nothing:
                    raise RuntimeError('value is not available')
                else:
                    return default
            return self.value
        finally:
            self.cv.release()

    def getvalue(self):
        self.cv.acquire()
        try:
            if not self.value_available:
                self.cv.wait()
            return self.value
        finally:
            self.cv.release()

    def setvalue(self, value):
        self.cv.acquire()
        try:
            if not self.value_available:
                self.value = value
                self.value_available = True
                self.cv.notifyAll()
        finally:
            self.cv.release()


@implementer(IWorker)
class Worker(object):
    def __init__(self, workers, maxsize=0):
        self.workers = workers
        self.running = True
        self.stopped = Future()
        self.fn = Queue(maxsize=maxsize)
        self.callbacks = []

    def run(self):
        while self.running:
            try:
                f = self.fn.get(timeout=1.)
                try:
                    f()
                finally:
                    self.workers.notify_done(self)
            except EmptyException:
                pass
        self.stopped.setvalue(True)
        for callback in self.callbacks:
            callback(self)

    def stop(self, callback):
        self.stopped.cv.acquire()
        try:
            if self.running:
                self.running = False
            if self.stopped.trygetvalue(False):
                callback()
            else:
                self.callbacks.append(callback)
        finally:
            self.stopped.cv.release()

    def __call__(self, fn, timeout=None):
        self.fn.put(fn, timeout=timeout)


def _spawn_thread(fn, name=None):
    t = threading.Thread(target=fn, name=name)
    t.start()
    return t


@implementer(IWorkers)
class Workers(object):
    def __init__(self, nworkers=1, spawner=_spawn_thread, worker_factory=Worker, poller=None):
        self.spawner = spawner
        self.supervisor = threading.Thread(target=self._supervisor, name='Supervisor')
        self.workers = [(None, None, None) for _ in range(nworkers)]
        self.available_workers = deque()
        self.worker_map = {}
        self.worker_factory = worker_factory
        self.poller = poller
        self.waiting_list = deque()
        self.command = Queue()

    def notify_done(self, worker):
        self.command.put(('notify_done', worker))

    def _supervisor(self):
        while True:
            command = self.command.get()
            logger.debug('command=%r' % (command, ))
            if command[0] == 'initialize':
                for i, (_, worker, _) in enumerate(self.workers):
                    if worker is None:
                        worker = self.worker_factory(self)
                        name = 'worker-%i' % i
                        self.workers[i] = (self.spawner(worker.run, name=name), worker, True)
                        self.worker_map[worker] = i
                        self.available_workers.append(worker)
                command[1].setvalue(True)
            elif command[0] == 'stop':
                count = [len(self.workers)]
                all_workers_stopped = Future() 
                def worker_stopped(worker):
                    logger.debug('worker %d stopped' % self.worker_map[worker])
                    count[0] -= 1
                    if count[0] == 0:
                        all_workers_stopped.setvalue(True)
                for _, worker, _ in self.workers:
                    worker.stop(worker_stopped)
                all_workers_stopped.getvalue()
                break
            elif command[0] == 'allocate':
                if len(self.available_workers) > 0:
                    worker = self.available_workers.popleft()
                    i = self.worker_map[worker]
                    self.workers[i] = (self.workers[i][0], worker, False)
                    command[1].setvalue(worker) 
                else:
                    self.waiting_list.append(command[1])
            elif command[0] == 'notify_done':            
                worker = command[1]
                i = self.worker_map[worker]
                if len(self.waiting_list) > 0:
                    f = self.waiting_list.popleft()
                    f.setvalue(worker)
                else:  
                    self.workers[i] = (self.workers[i][0], worker, True)
                    self.available_workers.append(worker)

    def dispatch(self, fn):
        f = Future()
        self.command.put(('allocate', f))
        def _():
            w = f.trygetvalue(None)
            if w is None:
                self.poller(_)
            else:
                w(fn)
        _()

    def start(self):
        self.supervisor.start()
        f = Future()
        self.command.put(('initialize', f))
        f.getvalue()
        logger.info('Supervisor is ready')

    def stop(self):
        self.command.put(('stop', ))
        self.supervisor.join()


class MServeCommand(object):
    def __init__(self, registry, consumer_names):
        self.registry = registry
        self.io_loop = ioloop.IOLoop.instance()
        self.consumers = self.setup_consumers(consumer_names)
        self.stop_signal = Future()
        self.all_consumer_closed = Future()
        for consumer in self.consumers:
            self.io_loop.add_callback(consumer.connect)
        self.workers = Workers(nworkers=1, spawner=lambda fn, **kwargs: None, worker_factory=lambda workers: self.sole_worker, poller=self._poller)
        self.sole_worker = Worker(self.workers)
        self.registry.registerUtility(self.workers, IWorkers)
        self.io_thr = threading.Thread(target=self.io, name='IOThread')
        self.hypervisor_thr = threading.Thread(target=self.hypervisor, name='Hypervisor')

    def setup_consumers(self, consumer_names):
        consumers = set()
        def closed(consumer):
            consumers.remove(consumer)
            if len(consumers) == 0:
                self.all_consumer_closed.setvalue(True)
        for consumer_name in consumer_names:
            consumer = get_consumer(self.registry, consumer_name)
            if consumer is None:
                raise ApplicationError("no such consumer: %s\n" % consumer_name)
            consumer.add_close_callback(closed)
            consumers.add(consumer)
        return consumers

    def io(self):
        self.io_loop.make_current()
        logger.info("IO thread started")
        self.io_loop.start()
        logger.info('IO thread ended')

    def hypervisor(self):
        self.stop_signal.getvalue()
        self.workers.stop()
        def _():
            for consumer in self.consumers:
                consumer.close()
        self.io_loop.add_callback(_)
        self.all_consumer_closed.getvalue()
        self.io_loop.stop()
        self.io_thr.join()

    def _poller(self, fn):
        self.io_loop.add_callback(lambda: self.io_loop.add_timeout(self.io_loop.time() + .2, fn))

    def run(self):
        self.io_thr.start()
        self.workers.start()
        self.hypervisor_thr.start()
        self.sole_worker.run() # worker runs in the main thread
        self.hypervisor_thr.join()


def build_option_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("consumers", nargs='+', default=['pika'])
    return parser

def main(args=sys.argv[1:]):
    parser = build_option_parser()
    args = parser.parse_args(args)

    setup_logging(args.config)
    app = get_app(args.config)
    registry = global_registries.last

    try:
        mserver = MServeCommand(registry, args.consumers)
        def _stop_handler(signum, frame):
            mserver.stop_signal.setvalue(True)
        signal.signal(signal.SIGTERM, _stop_handler)
        signal.signal(signal.SIGINT, _stop_handler)
        mserver.run()
    except ApplicationError as e:
        sys.stderr.write(e.message)
        sys.stderr.flush()
        return 1

if __name__ == '__main__':
    main()
