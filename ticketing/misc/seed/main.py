import os
import sys
from locale import getpreferredencoding
from fixtures import sites, organization_names, build_organization_datum, build_user_datum, service_data
from fixture import DataSuite, DataWalker, ReferenceGraph, SQLSerializer
from svggen import SVGGenerator, NESW
from lxml.etree import tostring
import logging

def main(argv):
    logging.basicConfig(level=getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO), stream=sys.stderr)
    suite = DataSuite()
    digraph = ReferenceGraph()
    walker = DataWalker(suite, digraph)

    for organization_datum in [build_organization_datum(name) for name in organization_names]:
        organization_datum.user_id=build_user_datum()
        logging.info("Resolving references...")
        walker(organization_datum)

    for service_datum in service_data:
        walker(service_datum)

    for site in sites:
        suite[site._schema].add(site)
        open('%08d.xml' % site.id, 'w').write(
            tostring(
                SVGGenerator(
                    seat_size=10,
                    margin=NESW(top=4., right=4., bottom=4., left=4.),
                    padding=NESW(top=4., right=4., bottom=4., left=4.),
                    row_margin=NESW(top=4., right=4., bottom=4., left=4.),
                )(site._config),
                pretty_print=True)
            )

    SQLSerializer(sys.stdout, encoding=getpreferredencoding())(suite, digraph)

if __name__ == '__main__':
    main(sys.argv)
