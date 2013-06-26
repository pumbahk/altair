import argparse
import sqlahelper
import sqlalchemy as sa
import sys
import logging

## for model dependency
import altaircms.page.models as p
import altaircms.asset.models
import altaircms.tag.models
import altaircms.event.models as e
import altaircms.models as m
from altaircms.page import api as papi
from altaircms.solr import api as sapi

logger = logging.getLogger(__name__)

def setup_db(dburl):
    engine = sa.create_engine(dburl)
    sqlahelper.add_engine(engine)

def sync_data_to_solr(server_url):
    ftsearch = sapi.SolrSearch(server_url)
    for page in p.Page.query:
        logger.info("Processing page %s" % page.title)
        doc = papi.doc_from_page(page)
        ftsearch.register(doc)
    ftsearch.commit()

def main():
    parser = argparse.ArgumentParser(description="sync page data to solr ")
    parser.add_argument("-c", "--config", help="configuration file")
    parser.add_argument("--dburl", help="db url. e.g. mysql+pymysql://foo:foo@localhost/foo (default: %(default)s)", default="sqlite://")
    parser.add_argument("--solrurl", help="solr url. e.g. http://localhost:8082/solr")
    args = parser.parse_args()
    _main(args)

def _main(args):
    if args.config:
        from pyramid.paster import bootstrap, setup_logging
        env = bootstrap(args.config)
        setup_logging(args.config)
        solrurl = args.solrurl or env['registry'].settings['altaircms.solr.server.url']
    else:
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
        setup_db(args.dburl)
        solrurl = args.solrurl
    return sync_data_to_solr(solrurl)

if __name__ == "__main__":
    main()
