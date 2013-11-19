import re
import os
from lxml import html
from io import BytesIO
from urlparse import urljoin
from functools import partial
import logging
logger = logging.getLogger(__name__)
from . import is_html_filename
# utility = IDirectoryResource


def has_doctype(doctype):
    ## lxml default doctype is below stmt.
    ## this is bad personally, but lxml always return doctype.
    return doctype != '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">'

def get_doctype(doc, encoding):
    doctype = doc.getroottree().docinfo.doctype.encode(encoding)
    if has_doctype(doctype):
        return doctype
    else:
        return None

STRIP_BEGIN_RX = re.compile('^\n?<html>\n?<body>(?:\n?<p>)?')
STRIP_END_RX = re.compile('(?:</p>\n?)?</body>\n?</html>\n?$')
def strip_extra_tags_if_just_text(output, begin_rx=STRIP_BEGIN_RX, end_rx=STRIP_END_RX):
    # logger.info("***{}".format(output[:20]))
    # logger.info("***{}".format(output[-20:]))
    # hmm.
    bm = begin_rx.search(output)
    if not bm:
        return output

    em = end_rx.search(output)
    if not em:
        return output
    return output[(bm.end()-bm.start()):-(em.end()-em.start())]

def rewrite_links_with_el(doc, link_repl_func, resolve_base_href=True,
                      base_href=None):
    if base_href is not None:
        # FIXME: this can be done in one pass with a wrapper
        # around link_repl_func
        doc.make_links_absolute(base_href, resolve_base_href=resolve_base_href)
    elif resolve_base_href:
        doc.resolve_base_href()
    for el, attrib, link, pos in doc.iterlinks():
        new_link = link_repl_func(el, link.strip())
        if new_link == link:
            continue
        if new_link is None:
            # Remove the attribute or element content
            if attrib is None:
                el.text = ''
            else:
                del el.attrib[attrib]
            continue
        if attrib is None:
            new = el.text[:pos] + new_link + el.text[pos+len(link):]
            el.text = new
        else:
            cur = el.attrib[attrib]
            if not pos and len(cur) == len(link):
                # Most common case
                el.attrib[attrib] = new_link
            else:
                new = cur[:pos] + new_link + cur[pos+len(link):]
                el.attrib[attrib] = new


## convert function
def doc_convert_from_s3link(doc, base_url, current_url):
    def link_repl(el, href):
        tag = el.tag.lower()
        if tag == "a" or tag == "script":
            return href

        if href.startswith("//"):
            href = "http:"+href
        if href.startswith(base_url):
            return os.path.relpath(href, os.path.dirname(current_url))
        return href
    rewrite_links_with_el(doc, link_repl)

def doc_convert_to_s3link(doc, base_url, convert=urljoin):
    def link_repl(el, href):
        tag = el.tag.lower()
        if tag == "a" or tag == "script":
            return href
        else:
            absolute_href = convert(base_url, href)
            absolute_href = absolute_href.replace("http:", "") #to: //foo.bar
            return absolute_href
    rewrite_links_with_el(doc, link_repl)

_PARSERS = {}
DEFAULT_ENCODING = "utf-8" #xxx:

def get_html_parser(encoding=DEFAULT_ENCODING):
    global _PARSERS
    parser = _PARSERS.get(encoding)
    if parser is None:
        parser = _PARSERS[encoding] = html.HTMLParser(encoding=encoding)
    return parser

## serialize/deserialize
def doc_from_filepath(path, subname, encoding):
    return html.parse(path, parser=get_html_parser(encoding)).getroot()

def doc_from_io(io, subname, encoding):
    return html.parse(io, parser=get_html_parser(encoding)).getroot()

def io_from_doc(doc, subname, encoding):
    doctype = get_doctype(doc, encoding)
    result = html.tostring(doc, pretty_print=True, encoding=encoding, doctype=doctype)
    result = strip_extra_tags_if_just_text(result)
    return BytesIO(result)

def string_from_doc(doc, subname, encoding):
    doctype = get_doctype(doc, encoding)
    result = html.tostring(doc, pretty_print=True, encoding=encoding, doctype=doctype)
    result = strip_extra_tags_if_just_text(result)
    return result

## apply refine function(a -> (dom -*> dom) -> b)
class HTMLFilter(object):
    def __init__(self, q, deserialize, serialize, encoding=DEFAULT_ENCODING):
        self.deserialize = deserialize
        self.serialize = serialize
        self.q = q or []
        self.encoding = encoding

    def add(self, f): # f is dom -> dom
        self.q.append(f)

    def __call__(self, io, subname, encoding=None):
        if not is_html_filename(subname):
            return io
        else:
            encoding = encoding or self.encoding
            doc = self.deserialize(io, subname, encoding=encoding)
            if doc is None:
                logger.warn("creating doc object is failure, from {subname}".format(subname=subname))
            for fn in self.q:
                doc = fn(doc, subname)
            return self.serialize(doc, subname, encoding=encoding)

HTMLFilterOutputIO = partial(HTMLFilter, deserialize=doc_from_io, serialize=io_from_doc)
HTMLFilterInputFilePathOutputString = partial(HTMLFilter, deserialize=doc_from_filepath, serialize=string_from_doc)


## api
def refine_link_on_upload(filename, dirname, utility, encoding=DEFAULT_ENCODING, convert=urljoin):
    base_url = utility.get_base_url(dirname, filename)
    def html_update(doc, subname):
        doc_convert_to_s3link(doc, base_url, convert=convert)
        return doc
    fil = HTMLFilterInputFilePathOutputString([html_update], encoding=encoding)
    path = os.path.join(dirname, filename)
    return fil(path, filename)

def refine_link_on_download_factory(static_page, utility, encoding=DEFAULT_ENCODING):
    root_url = utility.get_root_url(static_page)
    logger.info("download: uns3lize: '{}' -> ''".format(root_url))
    def html_update(doc, subname):
        doc_convert_from_s3link(doc, root_url, os.path.join(root_url, subname))
        return doc
    return HTMLFilterOutputIO([html_update])
