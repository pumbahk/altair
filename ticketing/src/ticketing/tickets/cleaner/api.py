import logging
logger = logging.getLogger(__name__)
from lxml import etree
from StringIO import StringIO

from . import cleanup_svg
from .normalize import normalize
from ..convert import to_opcodes


class TicketCleanerValidationError(Exception):
    pass

def skip_needless_part(string):
    comment_end_tag = "-->"
    if string.startswith(("<?xml", "<!--")) and comment_end_tag in string:
        return string[string.index(comment_end_tag)+len(comment_end_tag):]
    else:
        return string

def get_validated_xmltree(svgio, exc_class=TicketCleanerValidationError):
    try:
        return get_xmltree(svgio)
    except Exception, e:
        logger.exception(e)
        raise exc_class("xml: "+str(e))

def get_xmltree(svgio):
    xmltree = etree.parse(svgio)
    svgio.seek(0)
    return xmltree

#xxx: cleanup_svgはxmltreeを書き換えてしまう。なので２回呼び出すとおかしな結果になってしまう
def get_validated_svg_cleaner(svgio, exc_class=TicketCleanerValidationError):
    xmltree = get_validated_xmltree(svgio, exc_class=exc_class)
    result = TicketSVGValidator(exc_class=exc_class).validate(svgio, xmltree)
    return TicketSVGCleaner(svgio, xmltree, result=result)

class TicketSVGCleaner(object):
    def __init__(self, svgio, xmltree, io_create=StringIO, result=None):
        self.io_create = io_create
        self.svgio = svgio
        self.xmltree = xmltree
        self.result = result

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
        self.out = None

    def validate(self, svgio, xmltree):
        self._validate_on_cleanup_phase(xmltree)
        io = self.io_create()
        xmltree.write(io, encoding="UTF-8") #doc declaration?
        io.seek(0)
        self._validate_on_normalize_phase(svgio)
        svgio.seek(0)
        self._validate_on_converting_to_opcode(xmltree)
        return self.out

    def _validate_on_converting_to_opcode(self, xmltree):
        try:
            to_opcodes(xmltree)
        except Exception, e:
            logger.exception(e)
            raise self.exc_class("opcode:" + str(e))

    def _validate_on_cleanup_phase(self, xmltree):
        try:
            cleanup_svg(xmltree)
        except Exception, e:
            logger.exception(e)
            raise self.exc_class("cleanup: "+str(e))

    def _validate_on_normalize_phase(self, svgio):
        try:
            self.out = self.io_create()
            normalize(svgio, self.out, encoding="UTF-8")
        except Exception, e:
            logger.exception(e)
            raise self.exc_class("normalize: "+str(e))
