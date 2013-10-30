import sys
import unittest
from select import select
from socket import *
from socket import error as SocketError

EAGAIN = 35

class Timeout(Exception):
    pass

READ = 1
WRITE = 2
EXC = 3

def poll(s, event, timeout):
    x = ([], [], [], timeout)
    x[event - 1].append(s)
    y = select(*x)
    return x[0:3] == y

class RingBufferedIO(object):
    poller = staticmethod(poll)

    def __init__(self, s, recv_timeout=10, send_timeout=10, recv_buffer_size=4096):
        self.s = s
        self.recv_timeout = recv_timeout
        self.send_timeout = send_timeout
        self.recvbuf = bytearray(recv_buffer_size)
        self.recvbuf_head = 0
        self.recvbuf_avail = 0
        self.recv_eof = False
        self.send_eof = False

    def recv(self, n):
        recvbuf_len = len(self.recvbuf)

        if n > len(self.recvbuf):
            raise ValueError('n > %d' .recvbuf_len)

        recvbuf_head = self.recvbuf_head
        recvbuf_avail = self.recvbuf_avail

        recvbuf_tail = (recvbuf_head + recvbuf_avail) % recvbuf_len
        next_head = recvbuf_head + n
        first = True
        if recvbuf_head < recvbuf_tail or recvbuf_avail == 0:
            if next_head <= recvbuf_tail:
                chunk1 = self.recvbuf[recvbuf_head:next_head]
                chunk1_len = n
            else:
                if not self.recv_eof:
                    while recvbuf_len > recvbuf_tail:
                        if not first:
                            if not self.poller(self.s, READ, self.recv_timeout):
                                raise Timeout()
                        try:
                            nbytesread = self.s.recv_into(memoryview(self.recvbuf)[recvbuf_tail:recvbuf_len])
                            if nbytesread == 0:
                                self.recv_eof = True
                                break
                        except SocketError as e:
                            if e.errno != EAGAIN:
                                raise
                            nbytesread = 0
                        recvbuf_tail += nbytesread
                        first = False
                next_head = min(recvbuf_tail, next_head)
                chunk1 = self.recvbuf[recvbuf_head:next_head]
                chunk1_len = next_head - recvbuf_head
        else:
            if next_head <= recvbuf_len:
                chunk1 = self.recvbuf[recvbuf_head:next_head]
                chunk1_len = n
            else:
                chunk1 = self.recvbuf[recvbuf_head:]
                chunk1_len = recvbuf_len - recvbuf_head
                next_head = recvbuf_len
   
        rest = n - chunk1_len
        if rest > 0 and next_head > recvbuf_tail:
            if not self.recv_eof:
                while recvbuf_head > recvbuf_tail:
                    if not first:
                        if not self.poller(self.s, READ, self.recv_timeout):
                            raise Timeout()
                    try:
                        nbytesread = self.s.recv_into(memoryview(self.recvbuf)[recvbuf_tail:recvbuf_head])
                        if nbytesread == 0:
                            self.recv_eof = True
                            break
                    except SocketError as e:
                        if e.errno != EAGAIN:
                            raise
                        nbytesread = 0
                    recvbuf_tail += nbytesread
                    first = False
            next_head = min(recvbuf_tail, rest)
            chunk2 = self.recvbuf[0:next_head]
            retval = bytearray(chunk1_len + next_head)
            retval[0:chunk1_len] = chunk1
            retval[chunk1_len:] = chunk2
            recvbuf_head = next_head
        else:
            recvbuf_head = next_head
            retval = chunk1

        self.recvbuf_head = recvbuf_head = recvbuf_head % recvbuf_len
        self.recvbuf_avail = recvbuf_tail - recvbuf_head
        if self.recv_eof and len(retval) == 0:
            return None
        else:
            return retval

    def send(self, buf):
        if self.send_eof:
            return 0

        n = 0
        while n < len(buf):
            try:
                nbyteswritten = self.s.send(buf[n:])
                if nbyteswritten == 0:
                    self.send_eof = True
                    break
            except SocketError as e:
                if e.errno != EAGAIN:
                    raise
                nbyteswritten = 0
            n += nbyteswritten
            if not self.poller(self.s, WRITE, self.send_timeout):
                raise Timeout()

        return n

    def recv_until(self, chunk):
        recvbuf_len = len(self.recvbuf)

        chunk_len = len(chunk)
        if chunk_len > recvbuf_len:
            raise ValueError('len(chunk) > %d' % len(self.recvbuf))

        recvbuf_head = self.recvbuf_head
        recvbuf_avail = self.recvbuf_avail

        recvbuf_tail = recvbuf_head + recvbuf_avail

        first = True
        if recvbuf_tail <= recvbuf_len:
            while recvbuf_len >= recvbuf_tail:
                if chunk_len <= recvbuf_len - recvbuf_head:
                    n = self.recvbuf.find(chunk, recvbuf_head)
                    if n >= 0 and n + chunk_len <= recvbuf_tail:
                        retval = self.recvbuf[recvbuf_head:n + chunk_len]
                        self.recvbuf_head = recvbuf_head = n + chunk_len
                        self.recvbuf_avail = recvbuf_tail - recvbuf_head
                        return retval

                if self.recv_eof or recvbuf_tail == recvbuf_len:
                    break
                if not first:
                    if not self.poller(self.s, READ, self.recv_timeout):
                        raise Timeout()
                try:
                    nbytesread = self.s.recv_into(memoryview(self.recvbuf)[recvbuf_tail:])
                    if nbytesread == 0:
                        self.recv_eof = True
                        break
                except SocketError as e:
                    if e.errno != EAGAIN:
                        raise
                    nbytesread = 0
                recvbuf_tail += nbytesread
                first = False
            if recvbuf_tail < recvbuf_len:
                if recvbuf_head == recvbuf_tail:
                    return None
                retval = self.recvbuf[recvbuf_head:recvbuf_tail]
                self.recvbuf_head = recvbuf_tail
                self.recvbuf_avail = 0
                return retval
        recvbuf_tail %= recvbuf_len

        retval = bytearray(self.recvbuf[recvbuf_head:])
        recvbuf_head = 0
        while True:
            if chunk_len <= recvbuf_tail:
                n = self.recvbuf.find(chunk, 0)
                if n >= 0 and n + chunk_len <= recvbuf_tail:
                    recvbuf_head = n + chunk_len
                    break
            if not first:
                if not self.poller(self.s, READ, self.s):
                    raise Timeout()
            if recvbuf_tail == recvbuf_len:
                retval.extend(self.recvbuf[0:recvbuf_len])
                recvbuf_tail = 0
            if self.recv_eof:
                break
            try:
                nbytesread = self.s.recv_into(memoryview(self.recvbuf)[recvbuf_tail:])
                if nbytesread == 0:
                    self.recv_eof = True
                    recvbuf_head = recvbuf_tail
                    break
            except SocketError as e:
                if e.errno != EAGAIN:
                    raise
                nbytesread = 0
            recvbuf_tail += nbytesread
            first = False
        retval.extend(self.recvbuf[0:recvbuf_head])
        self.recvbuf_head = recvbuf_head
        self.recvbuf_avail = recvbuf_tail - recvbuf_head
        if self.recv_eof and len(retval) == 0:
            return None
        else:
            return retval

class TR310Protocol(object):
    def __init__(self, io, image):
        self.io = io
        self.state = self.initial
        self.image = image

    def initial(self):
        assert self.io.recv_until(b'\0') == b'READY\0'
        self.state = self.send_WS

    def send_WS(self):
        self.io.send('{WS|}')
        print self.io.recv_until(b'\x0d\x0a')
        self.state = self.send_JT

    def send_JT(self):
        self.io.send('{JT;131022131946|}{D1651,0630,1445|}{Y|}')
        print self.io.recv_until(b'\x0d\x0a')
        self.state = self.send_HD

    def send_HD(self):
        self.io.send('{HD001|}{WS|}')
        print self.io.recv_until(b'\x0d\x0a')
        self.state = self.send_C

    def send_C(self):
        self.io.send('{C|}')
        print self.io.recv_until('\x0d\x0a')
        self.state = self.send_SG

    def send_SG(self):
        self.io.send('{SG;0000D,0009D,0000,0000,2,')
        im = self.image.rotate(-90).convert('1')
        out = StringIO()
        im.save(out, 'bmp')
        print 'len=%d, prologue=%s' % (len(out.getvalue()), out.getvalue()[0:2])
        self.io.send(out.getvalue())
        self.io.send('|}')
        print self.io.recv_until(b'\x0d\x0a')
        self.state = self.send_WS2

    def send_WS2(self):
        self.io.send('{WS|}')
        print self.io.recv_until(b'\x0d\x0a')
        self.state = self.send_XS_IB

    def send_XS_IB(self):
        self.io.send('{XS;I,0001,0001C5010|}{IB|}')
        print self.io.recv_until(b'\x0d\x0a')
        self.state = None

    def next(self):
        if self.state is None:
            raise StopIteration
        self.state()

    def __iter__(self):
        return self

def main():
    s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
    s.connect((sys.argv[1], int(sys.argv[2])))
    s.setblocking(0)
    x = TR310Protocol(RingBufferedIO(s), image=Image.open('test.png'))
    for _ in x:
        pass

if __name__ == '__main__':
    class PollerTest(unittest.TestCase):
        def _callFUT(self, *args, **kwargs):
            return poll(*args, **kwargs)

        def test(self):
            pair = socketpair()
            self.assertFalse(self._callFUT(pair[1], READ, 0))
            self.assertTrue(self._callFUT(pair[0], WRITE, 0))
            self.assertEqual(4, pair[0].send("test"))
            self.assertTrue(self._callFUT(pair[1], READ, 0))

    class RingBufferedIOTest(unittest.TestCase):
        class DummySocket(object):
            def __init__(self, c="0123456789", l=None):
                self.offset = 0
                self.c = c
                if l is not None:
                    self.l = l
                else:
                    self.l = len(c)

            def recv_into(self, buf):
                l = min(self.l, len(buf))
                for i in range(0, l):
                    buf[i] = self.c[self.offset]
                    self.offset = (self.offset + 1) % len(self.c)
                self.l -= l
                return l

        def _makeOne(self, *args, **kwargs):
            target = RingBufferedIO(*args, **kwargs)
            target.poller = self.poller
            return target

        def dummy_poller(self, s, event, timeout):
            return True

        def setUp(self):
            self.poller = self.dummy_poller

        def test_recv1(self):
            dummy_socket = self.DummySocket(l=6)
            io = self._makeOne(dummy_socket, recv_buffer_size=10)
            self.assertEqual(io.recv(0), b'')
            self.assertEqual(io.recv(1), b'0')
            self.assertEqual(io.recv(2), b'12')
            self.assertEqual(io.recv(3), b'345')
            self.assertEqual(io.recv(0), None)
            
        def test_recv2(self):
            dummy_socket = self.DummySocket(l=5)
            io = self._makeOne(dummy_socket, recv_buffer_size=10)
            self.assertEqual(io.recv(0), b'')
            self.assertEqual(io.recv(1), b'0')
            self.assertEqual(io.recv(2), b'12')
            self.assertEqual(io.recv(3), b'34')
            self.assertEqual(io.recv(0), None)
            
        def test_recv3(self):
            dummy_socket = self.DummySocket(l=12)
            io = self._makeOne(dummy_socket, recv_buffer_size=10)
            self.assertEqual(io.recv(0), b'')
            self.assertEqual(io.recv(1), b'0')
            self.assertEqual(io.recv(2), b'12')
            self.assertEqual(io.recv(3), b'345')
            self.assertEqual(io.recv(4), b'6789')
            self.assertEqual(io.recv(5), b'01')
            self.assertEqual(io.recv(0), None)

        def test_recv4(self):
            dummy_socket = self.DummySocket(l=12)
            io = self._makeOne(dummy_socket, recv_buffer_size=8)
            self.assertEqual(io.recv(0), b'')
            self.assertEqual(io.recv(1), b'0')
            self.assertEqual(io.recv(2), b'12')
            self.assertEqual(io.recv(3), b'345')
            self.assertEqual(io.recv(4), b'6789')
            self.assertEqual(io.recv(5), b'01')
            self.assertEqual(io.recv(0), None)

        def test_recv_until1(self):
            dummy_socket = self.DummySocket(l=9)
            io = self._makeOne(dummy_socket, recv_buffer_size=8)
            self.assertEqual(io.recv_until(b'9'), b'012345678')
            self.assertEqual(io.recv_until(b'9'), None)

        def test_recv_until2(self):
            dummy_socket = self.DummySocket("0123456780123456789012345")
            io = self._makeOne(dummy_socket, recv_buffer_size=7)
            self.assertEqual(io.recv_until(b'9'), b'0123456780123456789')
            self.assertEqual(io.recv_until(b'9'), b'012345')
            self.assertEqual(io.recv_until(b'9'), None)

        def test_recv_until3(self):
            for n in range(2, 15):
                dummy_socket = self.DummySocket("01234567890123490123901239")
                io = self._makeOne(dummy_socket, recv_buffer_size=n)
                self.assertEqual(io.recv_until(b'9'), b'0123456789')
                self.assertEqual(io.recv_until(b'9'), b'012349')
                self.assertEqual(io.recv_until(b'9'), b'01239')
                self.assertEqual(io.recv_until(b'9'), b'01239')
                self.assertEqual(io.recv_until(b'9'), None)

    unittest.main() 
