# -*- coding:utf-8 -*-
from pyramid.paster import bootstrap
import transaction
from altaircms.page.models import Page
from altaircms.widget.tree.proxy import WidgetTreeProxy
from altaircms.models import DBSession
from collections import namedtuple
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

Classified = namedtuple("Classfied", "page, success, failure")


def classifiy(page):
    tree = WidgetTreeProxy(page)
    success, failure = [], []
    for list_of_widget in tree.blocks.values():
        for widget in list_of_widget:
            if widget.page_id is None or int(widget.page_id) == int(page.id):
                success.append(widget)
            else:
                failure.append(widget)
    return Classified(page=page, success=success, failure=failure)


def get_pages(organization_id):
    return Page.query.filter(Page.organization_id == organization_id).all()


def run(env, organization_id, is_execute):
    list_of_page = get_pages(organization_id)
    for page in list_of_page:
        classified = classifiy(page)
        if classified.failure:
            logger.info("page_id: %s", classified.page.id)
            for widget in classified.failure:
                logger.info("widget_id: %s,  page_id %s -> %s", widget.id, widget.page_id, page.id)
                if is_execute:
                    widget.page_id = page.id
                    DBSession.add(widget)


def main(argv):
    try:
        config = argv[1]
        organization_id = argv[2]
        env = bootstrap(config)
        sys.stderr.write("eaxactly execute command? Y or n")
        sys.stderr.flush()
        is_execute = sys.stdin.readline().strip() == "Y"
        logger.info("dry run is %s", not is_execute)
        return run(env, organization_id, is_execute)
        if is_execute:
            transaction.commit()
    except Exception as e:
        transaction.abort()
        logger.exception(e)

if __name__ == "__main__":
    import sys
    if sys.argv < 3:
        print("<> <config file> <organization id>")
    main(sys.argv)
