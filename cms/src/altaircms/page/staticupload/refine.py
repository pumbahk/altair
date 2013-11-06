import os
from lxml import html
from StringIO import StringIO
from urlparse import urljoin

def is_html_filename(filename):
    return filename.lower().endswith((".html", ".htm"))

## todo: support absolute url.
def _make_links_relative(doc, base_url, current_url):
    def link_repl(href):
        if href.startswith("//"):
            href = "http:"+href
        if href.startswith(base_url):
            return os.path.relpath(href, os.path.dirname(current_url))
        return href
    doc.rewrite_links(link_repl)

def _make_links_absolute(doc, base_url, resolve_base_href=True, convert=urljoin):
    if resolve_base_href:
        doc.resolve_base_href()
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

# string, string, <utility> -> <dom>
def refine_link(filename, dirname, utility, encoding=DEFAULT_ENCODING, convert=urljoin):
    path = os.path.join(dirname, filename)
    base_url = utility.get_base_url(dirname, filename)
    doc = html.parse(path, base_url=base_url, parser=get_html_parser(encoding)).getroot()
    if doc is not None:
        _make_links_absolute(doc, base_url, convert=convert)
    return doc

# string, string, <utility> -> string
def refine_link_as_string(filename, dirname, utility, encoding=DEFAULT_ENCODING, convert=urljoin):
    doc = refine_link(filename, dirname, utility, encoding=encoding, convert=convert)
    return html.tostring(doc, pretty_print=True, encoding=encoding) if doc is not None else ""

# string,  io, string -> string
def localize_filter(subname, io, base_url, encoding=DEFAULT_ENCODING):
    if not is_html_filename(subname):
        return io
    doc = html.parse(io, parser=get_html_parser(encoding)).getroot()
    if doc is not None:
        _make_links_relative(doc, base_url, os.path.join(base_url, subname))
    #hmm
    return StringIO(html.tostring(doc, pretty_print=True, encoding=encoding) if doc is not None else "")

