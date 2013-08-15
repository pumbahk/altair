import codecs

__all__ = [
    'cp932_normalized_tilde',
    'searcher',
    ]

cp932_codec = codecs.lookup('cp932')

def normalize_tildes(u):
    return u.replace(u'\uff5e', u'\u301c')

def cp932_normalized_tilde_decoder(s, errors='strict'):
    u, n = cp932_codec.decode(s, errors)
    return normalize_tildes(u), n

class CP932NormalizedTildeIncrementalDecoder(object):
    def __init__(self, errors='strict'):
        self.impl = cp932_codec.incrementaldecoder(errors)
        self.errors = errors

    def decode(self, s, final=False):
        return normalize_tildes(self.impl.decode(s, final))

    def reset(self):
        return self.impl.reset() 

class CP932NormalizedTildeStreamReader(codecs.Codec):
    def __init__(self, stream, errors='strict'):
        self.impl = cp932_codec.streamreader(stream, errors)
        self.errors = errors

    def encode(self, input, errors='strict'):
        return self.impl.encode(self, input, errors)

    def decode(self, input, errors='strict'):
        return cp932_normalized_tilde_decoder(input, errors)

    def read(self, size, chars, firstline):
        return normalize_tildes(self.impl.read(size, chars, firstline))

    def readline(self, size=None, keepends=True):
        retval = normalize_tildes(self.impl.readline(size))
        if not keepends:
            retval = retval.rstrip("\r\n")
        return retval

    def readlines(self, sizehint=None, keepends=True):
        if keepends:
            x = u""
        else:
            x = u"\r\n"
        return [normalize_tildes(line).rstrip(x) for line in self.impl.readline(sizehint, keepends)]

    def reset(self):
        return self.impl.reset()

cp932_normalized_tilde = codecs.CodecInfo(
    name='cp932:normalize-tilde',
    encode=cp932_codec.encode,
    decode=cp932_normalized_tilde_decoder,
    incrementalencoder=cp932_codec.incrementalencoder,
    incrementaldecoder=CP932NormalizedTildeIncrementalDecoder,
    streamreader=CP932NormalizedTildeStreamReader,
    streamwriter=cp932_codec.streamwriter)

def searcher(name):
    if name == 'cp932:normalized-tilde':
        return cp932_normalized_tilde
    return None

