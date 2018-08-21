#-*- coding: utf-8 -*-
import os
import csv
from .protocols import ALL
from .errors import ProtocolNotFound
from . import DEFAULT_ENCODING

class AugusParser(object):
    protocols = ALL

    @classmethod
    def is_protocol(cls, path):
        try:
            return cls.get_protocol(path)
        except ProtocolNotFound:
            return False

    @classmethod
    def get_protocol(cls, path):
        name = os.path.basename(path)
        for protocol in cls.protocols:
            if protocol.match_name(name):
                return protocol
        raise ProtocolNotFound(path)

    @classmethod
    def parse(cls, path, protocol=None):
        with open(path, 'rb') as fp:
            return cls.parsefp(fp, protocol)

    @classmethod
    def parsefp(cls, fp, protocol=None):
        if protocol is None:
            protocol = cls.get_protocol(fp.name)
        reader = csv.reader(fp)
        proto = cls.parserows(reader, protocol)
        proto.load_file_name(fp.name)
        return proto

    @classmethod
    def parserows(cls, rows, protocol, encoding=DEFAULT_ENCODING):
        def _dec(data):
            try:
                return data.decode(encoding)
            except (UnicodeEncodeError, UnicodeDecodeError) as err:
                raise err.__class__(repr(data), *err.args[1:])

        rows = map(lambda row: map(_dec, row), rows)
        proto = protocol()
        proto.load(rows)
        return proto
