import sys
import logging
import argparse
import threading
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
        self.fn = Queue(maxsize=maxsize)

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

    def stop(self):
        self.running = False

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
                for _, worker, _ in self.workers:
                    worker.stop()
                for t, _, _ in self.workers:
                    if t is not None:
                        t.join()
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

        self.poller(_)

    def start(self):
        self.supervisor.start()
        f = Future()
        self.command.put(('initialize', f))
        f.getvalue()

    def stop(self):
        self.command.put(('stop', ))

    def join(self):
        self.supervisor.join()


class MServeCommand(object):
    def __init__(self):
        self.parser = self.build_option_parser()

    def build_option_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("config")
        parser.add_argument("consumers", nargs='+', default=['pika'])
        return parser

    def run(self, args):
        args = self.parser.parse_args(args)

        setup_logging(args.config)
        app = get_app(args.config)
        registry = global_registries.last

        def io(io_loop, status):
            io_loop.make_current()
            logger.info("IO thread started")
            io_loop.start()
            logger.info('IO thread ended')
            status.setvalue(True)

        def hypervisor(status):
            status.getvalue()
            workers.stop()

        io_loop = ioloop.IOLoop.instance()
        for consumer_name in args.consumers:
            consumer = get_consumer(registry, consumer_name)
            if consumer is None:
                sys.stderr.write("no such consumer: %s\n" % consumer_name)
                sys.stderr.flush()
                return  1
            io_loop.add_callback(consumer.connect)

        sole_worker = None
        workers = Workers(nworkers=1, spawner=lambda fn, **kwargs: None, worker_factory=lambda workers: sole_worker, poller=lambda fn: io_loop.add_callback(lambda: io_loop.add_timeout(io_loop.time() + .2, fn)))
        registry.registerUtility(workers, IWorkers)
        sole_worker = Worker(workers)
        io_thr_status = Future()
        hypervisor_thr = threading.Thread(target=hypervisor, args=(io_thr_status,), name='HypervisorThread')
        io_thr = threading.Thread(target=io, args=(io_loop, io_thr_status,), name='IOThread')

        hypervisor_thr.start()
        workers.start()
        io_thr.start()
        try:
            sole_worker.run() # worker runs in the main thread
        except KeyboardInterrupt:
            io_loop.stop()
            
        workers.join()
        io_thr.join()
        hypervisor_thr.join()

        return 0 if io_thr_status.getvalue() else 1

def main(args=sys.argv[1:]):
    sys.exit(MServeCommand().run(args))


if __name__ == '__main__':
    main()
