#-*- coding: utf-8 -*-
import os
import csv
from .protocols import ALL
from .errors import ProtocolNotFound

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
    def parse(cls, path):
        with open(path, 'rb') as fp:
            return cls.parsefp(fp)

    @classmethod
    def parsefp(cls, fp, protocol=None):
        if protocol is None:
            protocol = cls.get_protocol(fp.name)
        reader = csv.reader(fp)
        return cls.parserows(reader, protocol)
                
    @classmethod
    def parserows(cls, rows, protocol):
        proto = protocol()
        proto.load(rows)
        return proto
