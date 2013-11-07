import os
from lxml import html
from urlparse import urljoin
from . import is_html_filename
# utility = IDirectoryResource


## todo: support absolute url.
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

def refine_link(filename, dirname, utility, encoding=DEFAULT_ENCODING, convert=urljoin):
    path = os.path.join(dirname, filename)
    base_url = utility.get_base_url(dirname, filename)
    doc = html.parse(path, base_url=base_url, parser=get_html_parser(encoding)).getroot()
    if doc is not None:
        _make_links_absolute(doc, base_url, convert=convert)
    return doc

def refine_link_as_string(filename, dirname, utility, encoding=DEFAULT_ENCODING, convert=urljoin):
    doc = refine_link(filename, dirname, utility, encoding=encoding, convert=convert)
    return html.tostring(doc, pretty_print=True, encoding=encoding) if doc is not None else ""
