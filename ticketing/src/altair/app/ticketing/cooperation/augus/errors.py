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

class AlreadyExist(AugusError):
    pass

class AugusDataImportError(AugusError):
    pass

class IllegalImportDataError(AugusError):
    pass

class AugusDataExportError(AugusError):
    pass

class AugusPerformanceNotFound(AugusDataExportError):
    pass

class AugusIntegrityError(AugusError):
    pass

class IllegalDataError(AugusError):
    pass

class DuplicateFileNameError(AugusError):
    pass

class DistributionExcutionError(AugusError):
    pass
