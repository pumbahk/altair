import os
import unittest
import socket
import errno
import heapq
import time
from select import select
import ssl
import tempfile
from OpenSSL import crypto
from pytz import UTC
from datetime import datetime, timedelta, date
import threading


class PriorityQueue(object):
    def __init__(self, items=[]):
        self.items = list(items)
        if len(items) > 0:
            heapq.heapify(self.items)

    def push(self, item):
        heapq.heappush(self.items, item)

    def pushpop(self, item):
        return heapq.heappushpop(self.items, item)

    def pop(self):
        return heapq.heappop(self.items)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

class Reader(object):
    def __init__(self, reactor, f, eof=None):
        self.q = []
        self.reactor = reactor
        self.f = f
        self.callback = None
        self.eof = eof

    def read_until(self, charset, callback):
        assert self.callback is None
        self._read_until(charset, callback, None, False)

    def _read_until(self, charset, callback, t, eof):
        if not eof:
            for j, ch in enumerate(self.q):
                for i, c in enumerate(ch):
                    if c in charset:
                        e = len(ch) - i
                        if e == 1:
                            v = b''.join(self.q[0:j + 1])
                            del self.q[0:j + 1]
                        else:
                            v = b''.join(self.q[0:j + 1])[0:-e + 1]
                            del self.q[0:j]
                            self.q[0] = self.q[0][-e + 1:]
                        self.callback = None
                        callback(self.reactor, self.f, t, v, False)
                        return
                else:
                    continue
                break
        else:
            v = b''.join(self.q)
            del self.q[:]
            self.callback = None
            callback(self.reactor, self.f, t, v, True)
            if self.eof is not None:
                self.eof(self.reactor, self.f, t)
            return

        def read(reactor, f, t):
            d = f.recv(4096)
            if len(d) != 0:
                self.q.append(d)
            self._read_until(charset, callback, t, len(d) == 0)
        self.callback = read
        self.reactor.on('r', self.f, read)

    def cancel(self):
        if self.callback is not None:
            self.reactor.cancel('r', self.f, self.callback)

class EventReactor(object):
    def __init__(self, watch=None):
        self.callbacks = {
            'r': {},
            'w': {},
            'x': {},
            'once': {},
            }
        self.callbacks_per_fd = {}
        self.timers = PriorityQueue()
        self.onces = []
        if watch is None:
            watch = lambda reactor: True
        self.watch = watch

    def on(self, event, f, callback):
        callbacks_for_f = self.callbacks[event].get(f)
        if callbacks_for_f is None:
            callbacks_for_f = self.callbacks[event][f] = set()
        if callback in callbacks_for_f:
            return
        callbacks_per_fd = self.callbacks_per_fd.get(f)
        if callbacks_per_fd is None:
            callbacks_per_fd = self.callbacks_per_fd[f] = {
                'r': set(),
                'w': set(),
                'x': set(),
                }
        callbacks_per_fd[event].add(callback)
        callbacks_for_f.add(callback)

    def cancel(self, event, f, callback=None):
        callbacks_for_f = self.callbacks[event].get(f)
        if callbacks_for_f is None:
            return
        if callback is not None:
            callbacks_for_f.remove(callback)
        else:
            callbacks_for_f.clear()
        if len(callbacks_for_f) == 0:
            del self.callbacks[event][f]
        callbacks_per_fd = self.callbacks_per_fd.get(f)
        assert callbacks_per_fd is not None
        if callback is not None:
            callbacks_per_fd[event].remove(callback)
        else:
            callbacks_per_fd[event].clear()

    def timer(self, t, callback):
        if isinstance(t, date):
            t = time.mktime(t.timetuple())
        self.timers.push((t, callback))

    def once(self, callback):
        if self.onces is None:
            self.onces = []
        self.onces.append(callback)

    def __call__(self):
        while self.watch(self):
            ct = time.time()
            if self.onces is not None:
                for once in self.onces:
                    once(self, ct)
                self.onces = []
            try:
                tev = self.timers.pop()
            except IndexError:
                tev = None
            if tev is not None:
                td = tev[0] - ct
            else:
                td = 1.
            readys = {'r': [], 'w': [], 'x': []}
            try:
                (
                    readys['r'],
                    readys['w'],
                    readys['x']
                    ) = \
                select(
                    self.callbacks['r'].keys(),
                    self.callbacks['w'].keys(),
                    self.callbacks['x'].keys(),
                    td
                    )
            except:
                raise
            if len(readys['r']) == 0 and len(readys['w']) == 0 and len(readys['x']) == 0:
                if tev is not None:
                    ct = tev[0]
                    tev[1](self, ct)
            else:
                self.timers.push(tev)
                ct = time.time()
                for e, fl in readys.items():
                    for f in fl:
                        callbacks_for_f = list(self.callbacks[e][f])
                        del self.callbacks[e][f]
                        self.callbacks_per_fd[f][e].clear()
                        for callback in callbacks_for_f:
                            callback(self, f, ct)
                            

class Future(object):
    def __init__(self):
        self.cv = threading.Condition()
        self.value = None 
        self.value_available = False

    def getvalue(self):
        self.cv.acquire()
        try:
            if not self.value_available:
                self.cv.wait()
            return self.value
        finally:
            self.cv.release()

    def setvalue(self, value):
        self.value = value
        self.cv.acquire()
        try:
            if not self.value_available:
                self.value_available = True
                self.cv.notifyAll()
        finally:
            self.cv.release()

class GuardedValue(object):
    def __init__(self, value=None):
        self.lock = threading.Lock()
        self.value = None

    def getvalue(self):
        try:
            self.lock.acquire()
            return self.value
        finally:
            self.lock.release()

    def setvalue(self, value):
        try:
            self.lock.acquire()
            self.value = value
        finally:
            self.lock.release()

class TestOurHTTPConnection(unittest.TestCase):
    def _generate_private_key(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        return key

    def _gen_x509(self, key, subject={}, issuer=None, not_before=None, not_after=None):
        if not_before is None:
            not_before = datetime.utcnow().replace(tzinfo=UTC)
        if not_after is None:
            not_after = datetime.utcnow().replace(tzinfo=UTC) + timedelta(days=365)
        crt = crypto.X509()
        crt.set_pubkey(key)
        _subject = crt.get_subject()
        for k, v in subject.items():
            setattr(_subject, k, v)
        if issuer is not None:
            if isinstance(issuer, crypto.X509Name):
                crt.set_issuer(issuer)
            else:
                _issuer = crt.get_issuer()
                for k, v in issuer.items():
                    setattr(_issuer, k, v)
        crt.set_notBefore(not_before.astimezone(UTC).strftime("%Y%m%d%H%M%SZ"))
        crt.set_notAfter(not_after.astimezone(UTC).strftime("%Y%m%d%H%M%SZ"))
        return crt

    def _gen_certificate(self, signer=None, **kwargs):
        k = self._generate_private_key()
        if signer is None:
            issuer = kwargs.get('subject')
        else:
            issuer = signer[1].get_issuer()
        crt = self._gen_x509(k, issuer=issuer, **kwargs)
        if signer is None:
            crt.sign(k, 'sha1')
        else:
            crt.sign(signer[0], 'sha1')
        return k, crt

    def _cert_and_key_as_file(self, pair, chains=[]):
        k, crt = pair
        f = tempfile.NamedTemporaryFile(delete=False)
        try:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, crt))
            f.write('\n')
            for _crt in chains:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, _crt))
                f.write('\n')
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
        finally:
            f.close()
        return f.name

    def _getTarget(self):
        from .httplib import OurHTTPSConnection
        return OurHTTPSConnection

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs) 

    def setUp(self):
        ca_cert = self._gen_certificate(subject=dict(C='JP', ST='Tokyo', L='Chiyoda', O='Snake Oil CA, LTD.', CN='ca@example.com'))
        server_cert = self._gen_certificate(signer=ca_cert, subject=dict(C='JP', ST='Tokyo', L='Chiyoda', O='Snake Oil CA, LTD.', CN='example.com'))
        client_cert = self._gen_certificate(signer=ca_cert, subject=dict(C='JP', ST='Tokyo', L='Chiyoda', O='Snake Oil CA, LTD.', CN='client@example.com'))
        self.ca_cert_file = self._cert_and_key_as_file(ca_cert)
        self.server_cert_file = self._cert_and_key_as_file(server_cert, chains=[ca_cert[1]])
        self.client_cert_file = self._cert_and_key_as_file(client_cert, chains=[ca_cert[1]])
        self.server_exc = None
        self.client_exc = None

    def tearDown(self):
        os.unlink(self.server_cert_file)
        os.unlink(self.client_cert_file)
        os.unlink(self.ca_cert_file)

    def _make_server(self, **kwargs):
        def _(fut, term):
            reactor = EventReactor(lambda reactor: not term.getvalue())
            def once(reactor, t):
                ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
                sss = ssl.wrap_socket(
                    ss,
                    certfile=self.server_cert_file,
                    ca_certs=self.ca_cert_file,
                    cert_reqs=ssl.CERT_REQUIRED,
                    **kwargs
                    )
                ss.bind(('127.0.0.1', 0))
                sss.listen(1)
                fut.setvalue(ss.getsockname())
                sss.setblocking(False)
                def accept(reactor, f, t):
                    try:
                        cs, csn = sss.accept()
                        def closer(reactor, t):
                            reactor.cancel('r', cs)
                            reactor.cancel('w', cs)
                            reactor.cancel('x', cs)
                            cs.close()
                        reactor.timer(time.time() + 5, closer)
                        rdr = Reader(reactor, cs)
                        def readline(reactor, f, t, l, eof):
                            if len(l.rstrip()) == 0:
                                def write(reactor, f, t):
                                    f.write("HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\ntest")
                                    f.close()
                                reactor.on('w', f, write) 
                            else:
                                if not eof:
                                    rdr.read_until("\n", readline)
                        rdr.read_until("\n", readline)
                    except Exception as e:
                        self.server_exc = e
                reactor.on('r', sss, accept)
            reactor.once(once)
            reactor()
        return _

    def _make_client(self, **kwargs):
        def _(fut, term):
            try:
                host, port = fut.getvalue()
                conn = self._makeOne(
                    host=host,
                    port=port,
                    cert_file=self.client_cert_file,
                    ca_certs=self.ca_cert_file,
                    cert_reqs=ssl.CERT_REQUIRED,
                    **kwargs
                    )
                conn.request('GET', '/')
                resp = conn.getresponse()
                try:
                    self.assertEqual(resp.read(), 'test')
                finally:
                    resp.close()
            except Exception as e:
                self.client_exc = e
            finally:
                term.setvalue(True)
        return _

    def testSuccess(self):
        fut = Future()
        term = GuardedValue(False)

        st = threading.Thread(
            target=self._make_server(ssl_version=ssl.PROTOCOL_TLSv1),
            kwargs=dict(
                fut=fut,
                term=term)
            )
        st.start()
        ct = threading.Thread(
            target=self._make_client(ssl_version=ssl.PROTOCOL_TLSv1),
            kwargs=dict(
                fut=fut,
                term=term
                )
            )
        ct.start()

        st.join()
        ct.join()

        self.assertIsNone(self.server_exc)
        self.assertIsNone(self.client_exc)

    def testFail(self):
        fut = Future()
        term = GuardedValue(False)

        st = threading.Thread(
            target=self._make_server(ssl_version=ssl.PROTOCOL_TLSv1),
            kwargs=dict(
                fut=fut,
                term=term)
            )
        st.start()
        ct = threading.Thread(
            target=self._make_client(ssl_version=ssl.PROTOCOL_SSLv3),
            kwargs=dict(
                fut=fut,
                term=term
                )
            )
        ct.start()

        st.join()
        ct.join()

        self.assertIsInstance(self.server_exc, ssl.SSLError)
        self.assertIsInstance(self.client_exc, ssl.SSLError)

