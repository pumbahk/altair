#-*- coding: utf-8 -*-

class AugusError(Exception):
    pass

class ProtocolNotFound(AugusError):
    pass

class ProtocolFormatError(AugusError):
    pass
