# -*- coding:utf-8 -*-
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse

from pyramid.paster import bootstrap

def main():
    parser = argparse.ArgumentParser(description="renweal a position of data about static pageset. using hash(uuid4)")
    parser.add_argument("config", help=u"development.ini'")
    args = parser.parse_args()
    _main(args)


def _main(args):
    from altaircms.models import DBSession
    from altaircms.auth.models import Organization
    from altaircms.page.models import StaticPage
    from altaircms.page.staticupload.api import get_static_page_utility
    from altaircms.page.staticupload.subscribers import _update_model_file_structure


    OMAP = {}
    def get_organization(sp):
        if OMAP.get(sp.organization_id) is None:
             OMAP[sp.organization_id] = Organization.query.filter_by(id=sp.organization_id).one()
        return OMAP[sp.organization_id]

    env = bootstrap(args.config)
    request = env["request"]
    static_directory = get_static_page_utility(request)
    now = datetime.now()
    for sp in StaticPage.query.filter_by(uploaded_at=None):
        try:
            request.organization = get_organization(sp)
            absroot = static_directory.get_rootname(sp)
            _update_model_file_structure(sp, absroot)
            sp.uploaded_at = now
            DBSession.add(sp)
            sys.stderr.write(".")
        except Exception as e:
            logger.error(str(e))
    import transaction
    transaction.commit()
        
if __name__ == "__main__":
    main()
