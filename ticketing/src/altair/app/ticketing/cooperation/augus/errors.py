#-*- coding: utf-8 -*-
class AugusError(Exception):
    pass

class BadRequest(AugusError):
    pass
    
class NoSeatError(AugusError):
    pass
