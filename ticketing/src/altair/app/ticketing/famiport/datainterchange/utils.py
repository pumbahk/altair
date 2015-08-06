import os

def make_room(base_dir): 
    def _(dir_, serial=0):
        if os.path.exists(dir_):
            next_dir = '%s.%d' % (base_dir, serial)
            _(next_dir, serial + 1)
            os.rename(dir_, next_dir)
    _(base_dir)


class BufferedIOWrapper(object):
    def __init__(self, f, chunk_size=4096):
        self.f = f
        self.b = b''
        self.chunk_size = chunk_size

    def read_up_to(self, s, n=None):
        while True:
            if n is not None and len(self.b) >= n:
                retval = self.b[:n]
                self.b = self.b[i + n:]
                return retval
            i = self.b.index(s)
            if i >= 0:
                retval = self.b[:i]
                self.b = self.b[i + len(s):]
                return retval
            b = self.f.read(self.chunk_size)
            if b == b'':
                retval = self.b 
                self.b = b''
                return retval
            self.b += b

    def read(self, n):
        while True:
            if len(self.b) >= n:
                retval = self.b[:n]
                self.b = self.b[n:]
                return retval
            b = self.f.read(self.chunk_size)
            if b == b'':
                retval = self.b
                self.b = b''
                return retval
            self.b += b
