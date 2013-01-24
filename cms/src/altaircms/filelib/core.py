import logging
import os
import tempfile
logger = logging.getLogger(__name__)

from zope.interface import implementer, provider
from altaircms.filelib.interfaces import IUploadFile, IFileSession

from shutil import copyfileobj


from collections import namedtuple
SignaturedFile = provider(IUploadFile)(namedtuple("File", "name signature handler"))
File = provider(IUploadFile)(namedtuple("File", "name handler"))


@implementer(IFileSession)
class FileSession(object):
    def __init__(self, prefix="", make_path=None):
        if make_path is None:
            self.make_path = lambda : os.path.abspath(prefix)
        else:
            self.make_path = make_path
        self.pool = []

    def abspath(self, part):
        return os.path.join(self.make_path(), part)

    def add(self, uploadfile):
        if hasattr(uploadfile, "signature"):
            signatured_file = uploadfile
        else:
            signatured_file = self._write_to_tmppath(uploadfile)
        self.pool.append(signatured_file)
        return signatured_file

    def commit(self):
        for signatured_file in self.pool:
            try:
                realpath = os.path.join(self.make_path(), signatured_file.name)
                os.rename(signatured_file.signature, realpath)
                logger.debug("filesession. rename: %s -> %s" % (signatured_file.signature, realpath))
            except OSError, e:
                logger.warn("%s is not renamed" % signatured_file)
                logger.exception(str(e))
            except Exception, e:
                logger.exception(str(e))

    def _write_to_tmppath(self, uploadfile):
        path = tempfile.mktemp() #suffix?
        self.write_to_path(path, uploadfile.handler)
        return SignaturedFile(name=uploadfile.name, 
                                    handler=uploadfile.handler, 
                                    signature=path)

    def write_to_path(self, path, handler, option="w"):
        name = getattr(handler, "name", "<stream>")
        with open(path, option) as wf:
            logger.debug("FileSession: write file. %s -> %s" % (name, path))
            copyfileobj(handler, wf)
