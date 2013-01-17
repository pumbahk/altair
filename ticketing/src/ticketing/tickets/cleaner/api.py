# -*- coding:utf-8 -*-
import re
import logging
logger = logging.getLogger(__name__)
from lxml import etree
from StringIO import StringIO

from . import cleanup_svg
from .normalize import normalize
from ..convert import to_opcodes


class TicketCleanerValidationError(Exception):
    pass

def get_validated_xmltree(svgio, exc_class=TicketCleanerValidationError):
    try:
        return get_xmltree(svgio)
    except Exception, e:
        logger.exception(e)
        raise exc_class("xml: "+str(e))

def get_xmltree(svgio):
    svgio = skip_needless_content(svgio)
    xmltree = etree.parse(svgio)
    svgio.seek(0)
    return xmltree

def _get_line(inp, eof=""):
    line = inp.readline()
    if line == eof:
        raise Exception("input source is empty")
    return line

def _skip_needless_part(inp, beg, end):
    pos = inp.tell()
    line = _get_line(inp)
    while skip_white_space_rx.match(line):
        pos = inp.tell()
        line = _get_line(inp)
    mb = beg.search(line)
    if mb:
        me = end.search(line)
        if me:
            pos += me.end()
        else:
            while True:
                pos = inp.tell()
                line = _get_line(inp)
                me = end.search(line)
                if me:
                    pos += me.end()
                    break
    inp.seek(pos)
    return inp

skip_prologue_rx_pair = (re.compile(r'<\?xml'), re.compile(r'\?>'))
skip_comment_rx_pair = (re.compile(r'<!--'), re.compile(r'-->'))
skip_white_space_rx = re.compile("[ \t]*$")
def skip_needless_content(inp):
    inp = _skip_needless_part(inp, *skip_prologue_rx_pair)
    inp = _skip_needless_part(inp, *skip_comment_rx_pair)
    inp = _skip_needless_part(inp, *skip_prologue_rx_pair)
    inp = _skip_needless_part(inp, *skip_comment_rx_pair)
    return inp


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
