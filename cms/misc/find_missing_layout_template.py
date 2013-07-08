# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse
from pyramid.paster import bootstrap


def main():
    parser = argparse.ArgumentParser(description="finding missing layout template files.")
    parser.add_argument("config", help=u"development.ini'")
    args = parser.parse_args()
    _main(args)

class OMAP(object):
    def __init__(self, model):
        self.model = model
        self.map = {}
    def get(self, organization_id):
        k = unicode(organization_id)
        org = self.map.get(k)
        if org is None:
            self.map[k] = org = self.model.query.filter_by(id=k).one()
        return org

def _main(args):
    from altaircms.layout.models import Layout
    from altaircms.auth.models import Organization
    from altairsite.front import install_resolver
    from altairsite.front.api import get_frontpage_discriptor_resolver
    omap = OMAP(Organization)
    env = bootstrap(args.config)
    request = env["request"]
    class config:
        registry = env["registry"]

    install_resolver(config)
    layouts = Layout.query.filter(Layout.organization_id!=None).all()
    for layout in layouts:
        assert layout.organization_id
        request.organization = omap.get(layout.organization_id)
        resolver = get_frontpage_discriptor_resolver(request)
        descriptor = resolver.resolve(request, layout, verbose=True)
        if not descriptor.exists():
            print descriptor.abspath()
    
if __name__ == "__main__":
    main()
