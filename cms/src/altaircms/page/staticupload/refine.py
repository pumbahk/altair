import os
from lxml import html
from StringIO import StringIO
from urlparse import urljoin
from functools import partial
import logging
logger = logging.getLogger(__name__)

def is_html_filename(filename):
    return filename.lower().endswith((".html", ".htm"))


## convert function
def doc_convert_from_s3link(doc, base_url, current_url):
    def link_repl(href):
        if href.startswith("//"):
            href = "http:"+href
        if href.startswith(base_url):
            return os.path.relpath(href, os.path.dirname(current_url))
        return href
    doc.rewrite_links(link_repl)

def doc_convert_to_s3link(doc, base_url, convert=urljoin):
    def link_repl(href):
        if href.endswith(".js"):
            return href
        elif is_html_filename(href) or href.endswith("/") or os.path.splitext(href)[1] == "":
            return href
        else:
            absolute_href = convert(base_url, href)
            if href.startswith("//"):
                absolute_href = absolute_href.replace("http:", "")
            return absolute_href
    doc.rewrite_links(link_repl)

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
    return StringIO(html.tostring(doc, pretty_print=True, encoding=encoding))

def string_from_doc(doc, subname, encoding):
    return html.tostring(doc, pretty_print=True, encoding=encoding)


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
