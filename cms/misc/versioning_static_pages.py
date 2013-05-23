# -*- coding:utf-8 -*-
import os
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse
import transaction
from pyramid.paster import bootstrap

## s3にはあげていない

def main():
    parser = argparse.ArgumentParser(description="foo -> foo/20/", formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("config", help=u"development.ini'")
    args = parser.parse_args()
    _main(args)

def switch_path(src, page):
    ## slackoff
    basedir = os.path.dirname(src)
    TMP = os.path.join(basedir, "__tmp__")
    os.mkdir(TMP)
    os.rename(src, os.path.join(TMP, unicode(page.id)))
    os.rename(TMP, src)

def _main(args):
    from alatircms.models import Organization
    from alatircms.models import DBSession
    from alatircms.page.models import StaticPage
    from altaircms.page.staticupload.api import get_static_page_utility
    from altaircms.page.staticupload.directory_resources import AfterCreate
    from altaircms.page.staticupload.subscribers import _update_model_file_structure

    OMAP = {}
    class DummyRequest(object):
        def __init__(self, registry, static_page):
            self._o = static_page
            self.registry = registry
            self.organization = OMAP.get(static_page.organization_id)
            if self.organization_id is None:
                self.organization = OMAP[static_page.organization_id] = Organization.query.filter_by(id=static_page.organization_id).one()

    try:
        env = bootstrap(args.config)
        registry = env["registry"]
        pages = StaticPage.query.all()
        for p in pages:
            request = DummyRequest(registry, p)
            static_directory = get_static_page_utility(request)
            absroot = static_directory.get_root_name(p)
            if os.path.exists(absroot):
                continue
            prev_root = os.path.dirname(absroot)
            if not os.path.exists(prev_root):
                logger.warn("{0} is not found. ignored.")
                continue
            switch_path(prev_root, p)
            request.registry.notify(AfterCreate(request, static_directory, absroot))
            _update_model_file_structure(p, absroot)
            DBSession.add(p)
            ## refine, s3upload
        transaction.commit()
    except Exception, e:
        logger.exception(str(e))
        transaction.abort()
