from StringIO import StringIO
from . import cleanup_svg
from .normalize import normalize
from ..convert import to_opcodes

class TicketCleanerValidationError(Exception):
    pass

class TicketSVGCleaner(object):
    def __init__(self, svgio, xmltree, io_create=StringIO):
        self.io_create = io_create
        self.svgio = svgio
        self.xmltree = xmltree
        self.result = None

    def get_cleaned_svgio(self):
        if self.result:
            return self.result

        io = self.io_create()
        cleanup_svg(self.xmltree)
        self.xmltree.write(io, encoding="UTF-8") #doc declaration?

        io.seek(0)

        self.result = self.io_create()
        normalize(io, self.result, encoding="UTF-8")
        return self.result

class TicketSVGValidator(object):
    def __init__(self, exc_class=TicketCleanerValidationError, io_create=StringIO):
        self.exc_class = exc_class
        self.io_create = io_create

    def validate(self, svgio, xmltree):
        self._validate_on_cleanup_phase(xmltree)
        self._validate_on_normalize_phase(svgio)
        svgio.seek(0)
        self._validate_on_converting_to_opcode(xmltree)
        return True

    def _validate_on_converting_to_opcode(self, xmltree):
        try:
            to_opcodes(xmltree)
        except Exception, e:
            raise self.exc_class("opcode:" + str(e))

    def _validate_on_cleanup_phase(self, xmltree):
        try:
            cleanup_svg(xmltree)
        except Exception, e:
            raise self.exc_class("cleanup: "+str(e))

    def _validate_on_normalize_phase(self, svgio):
        try:
            out = self.io_create()
            normalize(svgio, out, encoding="UTF-8")
        except Exception, e:
            raise self.exc_class("normalize: "+str(e))
