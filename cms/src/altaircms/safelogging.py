import logging

class SafeLoggingWrapper(object):
    def __init__(self, logger):
        self.logger = logger
        
    def coerce(self, msg):
        try:
            if isinstance(msg, (str, unicode)):
                return msg.encode("utf-8", errors="replace")
            return self.coerce(str(msg))
        except UnicodeDecodeError:
            return repr(msg)
        except Exception as e:
            return str(e)
        
    def info(self, msg, *args, **kwargs):
        return self.logger.info(self.coerce(msg), *args, **kwargs)
    def debug(self, msg, *args, **kwargs):
        return self.logger.debug(self.coerce(msg), *args, **kwargs)
    def log(self, msg, *args, **kwargs):
        return self.logger.log(self.coerce(msg), *args, **kwargs)
    def warn(self, msg, *args, **kwargs):
        return self.logger.warn(self.coerce(msg), *args, **kwargs)
    def error(self, msg, *args, **kwargs):
        return self.logger.error(self.coerce(msg), *args, **kwargs)
    def exception(self, msg, *args, **kwargs):
        return self.logger.exception(self.coerce(msg), *args, **kwargs)

def getLogger(*args, **kwargs):
    logger = logging.getLogger(*args, **kwargs)
    return SafeLoggingWrapper(logger)
