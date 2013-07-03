# -*- coding:utf-8 -*-
import os
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse
import transaction
from pyramid.paster import bootstrap
import sys
import shutil
from urlparse import urljoin
import functools

def renwal_file(request, static_page, src, dst):
    from altaircms.page.staticupload.refine import refine_link_as_string
    from altaircms.page.staticupload.api import get_static_page_utility
    ext = os.path.splitext(src)[1]
    dirname = os.path.dirname(dst)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if not ext in (".html", ".mako", ".htm"):
        shutil.copy2(src, dst)
    else:
        static_directory = get_static_page_utility(request)
        with open(dst, "w") as wf:
            dirname, filename = os.path.split(src)
            def convert(base_href, href):
                return href.replace("/{0}/".format(static_page.name), "/{0}/{1}/".format(static_page.name,unicode(static_page.id)), 1)
            wf.write(refine_link_as_string(filename, dirname, static_directory, convert=convert))

def renewal(request, absroot, old_absroot, static_page):
    q = []
    if not os.path.exists(absroot):
        os.makedirs(absroot)
    for root, ds, fs in os.walk(old_absroot):
        for f in fs:
            q.append(functools.partial(renwal_file, request, static_page, os.path.join(root, f), os.path.join(root.replace(old_absroot, absroot), f)))
    for f in q:
        f()


def main():
    parser = argparse.ArgumentParser(description="foo -> foo/20/", formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("config", help=u"development.ini'")
    args = parser.parse_args()
    _main(args)

def _main(args):
    from altaircms.auth.models import Organization
    from altaircms.page.models import StaticPage
    from altaircms.page.staticupload.api import get_static_page_utility

    OMAP = {}
    class DummyRequest(object):
        def __init__(self, registry, static_page):
            self._o = static_page
            self.registry = registry
            self.organization = OMAP.get(static_page.organization_id)
            if self.organization is None:
                self.organization = OMAP[static_page.organization_id] = Organization.query.filter_by(id=static_page.organization_id).one()


    try:
        env = bootstrap(args.config)
        registry = env["registry"]
        pages = StaticPage.query.filter_by(organization_id=8).all()
        for p in pages:
            sys.stderr.write(".")
            request = DummyRequest(registry, p)
            static_directory = get_static_page_utility(request)
            old_absroot = static_directory.get_obsolute_rootname(p)
            absroot = static_directory.get_rootname(p)

            if os.path.exists(old_absroot):
                cache_file = os.path.join(old_absroot, ".uploaded")
                if os.path.exists(cache_file):
                    print "skip:"+absroot
                    # continue
                open(cache_file, "w").close()
                renewal(request, absroot, old_absroot, p)
        transaction.commit()
    except Exception, e:
        logger.exception(str(e))
        transaction.abort()

if __name__ == "__main__":
    main()
