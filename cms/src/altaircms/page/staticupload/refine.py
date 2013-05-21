import os
from lxml import html
from urlparse import urljoin
# utility = IDirectoryResource

def _make_links_absolute(doc, base_url, resolve_base_href=True):
    if resolve_base_href:
        doc.resolve_base_href()
    def link_repl(href):
        if href.endswith(".js"):
            return href
        elif href.lower().endswith((".html", ".htm", "/")) or os.path.splitext(href)[1] == "":
            return href
        else:
            return urljoin(base_url, href)
    doc.rewrite_links(link_repl)

def refine_link(filename, dirname, utility):
    path = os.path.join(dirname, filename)
    base_url = utility.get_base_url(dirname, filename)
    doc = html.parse(path, base_url=base_url).getroot()
    if doc is not None:
        _make_links_absolute(doc, base_url)
    return doc

def refine_link_as_string(filename, dirname, utility):
    doc = refine_link(filename, dirname, utility)
    return html.tostring(doc) if doc is not None else ""
