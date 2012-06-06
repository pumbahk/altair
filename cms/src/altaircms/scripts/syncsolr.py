import argparse
import sqlahelper
import sqlalchemy as sa
import sys

## for model dependency
import altaircms.page.models as p
import altaircms.asset.models
import altaircms.tag.models
import altaircms.event.models as e
import altaircms.models as m
from altaircms.page import api as papi
from altaircms.solr import api as sapi

def setup(dburl):
    engine = sa.create_engine(dburl)
    sqlahelper.add_engine(engine)
    return

def sync_data_to_solr(server_url):
    ftsearch = sapi.SolrSearch(server_url)
    for page in p.Page.query:
        sys.stdout.write(".") ##
        sys.stdout.flush() ##
        doc = papi.doc_from_page(page)
        ftsearch.register(doc)
    ftsearch.commit()

def main():
    parser = argparse.ArgumentParser(description="sync page data to solr ")
    parser.add_argument("--dburl", help="db url. e.g. mysql+pymysql://foo:foo@localhost/foo (default: %(default)s)", default="sqlite://")
    parser.add_argument("--solrurl", help="solr url. e.g. http://localhost:8080/solr")
    args = parser.parse_args()
    _main(args)

def _main(args):
    setup(args.dburl)
    return sync_data_to_solr(args.solrurl)

if __name__ == "__main__":
    main()
