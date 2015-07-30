# -*- coding:utf-8 -*-
import re
import logging
from tempfile import mktemp
from shutil import copyfileobj

logger = logging.getLogger(__name__)
from lxml import etree
from StringIO import StringIO

from altair.svg.constants import SVG_NAMESPACE
from altair.app.ticketing.sej.ticket import TicketDataLargeError
from . import cleanup_svg
from .normalize import normalize
from ..constants import TS_SVG_EXT_NAMESPACE, INKSCAPE_NAMESPACE
from ..convert import convert_svg
from altair.app.ticketing.sej.ticket import SejTicketDataXml


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
#todo: refactoring;
def get_validated_svg_cleaner(svgio, exc_class=TicketCleanerValidationError, sej=False):
    xmltree = get_validated_xmltree(svgio, exc_class=exc_class)
    qr_code_emitter = QRCodeEmitter(xmltree)
    qr_code_emitter.emit()
    result = TicketSVGValidator(exc_class=exc_class, sej=sej).validate(xmltree)
    return TicketSVGCleaner(xmltree, result=result, vars_defaults=qr_code_emitter.vars_defaults)


class QRCodeEmitter(object):
    def __init__(self, xmltree):
        self.xmltree = xmltree
        self.vars_defaults = {}

    def emit(self):
        targets = self.xmltree.xpath('//n:rect[starts-with(@id, "QR")]', namespaces={"n": SVG_NAMESPACE})
        for target in targets:
            target.tag = "{{{ns}}}qrcode".format(ns=TS_SVG_EXT_NAMESPACE)
            attr_name = "{{{ns}}}label".format(ns=INKSCAPE_NAMESPACE)
            content = target.attrib[attr_name]
            target.attrib["content"] = u"{content}".format(content=content)

            ## need prefix?
            self.vars_defaults[content] = content

            if "style" in target.attrib:
                target.attrib.pop("style")
            if not "eclevel" in target.attrib:
                target.attrib["eclevel"] = "m"
        return self.xmltree

class TicketSVGCleaner(object):
    def __init__(self, xmltree, io_create=StringIO, vars_defaults={}, result=None):
        self.io_create = io_create
        self.xmltree = xmltree
        self.result = result
        self.vars_defaults = vars_defaults

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

def invalid_svg_upload_when_save(io, suffix=".svg"):
    pos = io.tell()
    io.seek(0)
    savepath = mktemp(suffix)
    logger.warn("invalid svg is uploaded. save as %s" % savepath)
    try:
        with open(savepath, "wb") as wf:
            copyfileobj(io, wf)
    except Exception, e:
        logger.error(str(e))
    io.seek(pos)
    

class TicketSVGValidator(object):
    def __init__(self, exc_class=TicketCleanerValidationError, io_create=StringIO, sej=False):
        self.exc_class = exc_class
        self.io_create = io_create
        self.sej = sej

    def validate(self, xmltree):
        default_io = None
        try:
            default_io = io = self._validated_io_on_cleanup_phase(xmltree)
            io = self._validated_io_on_normalize_phase(io)
            if self.sej:
                self._validate_on_converting_to_sej_xml(etree.parse(io))
            io.seek(0)
            return io
        except Exception:
            if default_io is None:
                default_io = self.io_create()
                xmltree.write(default_io, encoding="UTF-8")
            invalid_svg_upload_when_save(default_io, suffix=".svg")
            raise

        
    def _validated_io_on_cleanup_phase(self, xmltree):
        try:
            cleanup_svg(xmltree)
            out = self.io_create()
            xmltree.write(out, encoding="UTF-8")
            out.seek(0)
            return out
        except Exception, e:
            logger.exception(e)
            raise self.exc_class("cleanup: "+str(e))

    def _validated_io_on_normalize_phase(self, svgio):
        try:
            out = self.io_create()
            normalize(svgio, out, encoding="UTF-8")
            out.seek(0)
            return out
        except Exception, e:
            logger.exception(e)
            raise self.exc_class("normalize: "+str(e))

    def _validate_on_converting_to_sej_xml(self, xmltree):
        try:
            SejTicketDataXml(etree.tostring(convert_svg(xmltree), encoding=unicode)).validate()
        except UnicodeEncodeError, e:
            err = str(e)
            raise self.exc_class(u"不正な文字列が入っています。Unicode「{0}」".format(err[err.index('character'):].split("\'")[1]))
        except TicketDataLargeError, e:
            logger.exception(e)
            raise self.exc_class(u"チケットデータのサイズが制限を超えています。")
        except Exception, e:
            logger.exception(e)
            raise self.exc_class("sej_xml:" + e)