#-*- coding: utf-8 -*-
import os
from . import protocols
from .errors import ProtocolNotFound

def get_protocol(path):
    name = os.path.basename(path)
    for protocol in protocols.ALL:
        if protocol.match_name(name):
            return protocol
    raise ProtocolNotFound('Cannnot found the protocol: {0}'\
                           .format(name))
