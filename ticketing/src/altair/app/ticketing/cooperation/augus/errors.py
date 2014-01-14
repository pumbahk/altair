#-*- coding: utf-8 -*-
class AugusError(Exception):
    pass

class BadRequest(AugusError):
    pass
    
class NoSeatError(AugusError):
    pass
    
class AbnormalTimestampFormatError(AugusError):
    pass

class EntryFormatError(AugusError):
    pass

class SeatImportError(AugusError):
    pass    

