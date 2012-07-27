import os
import sys
from locale import getpreferredencoding
from fixtures import FixtureBuilder
from tableau import DataSuite, DataWalker
from tableau.sql import SQLGenerator
from svggen import SVGGenerator, NESW
from lxml.etree import tostring
import logging
from cProfile import run
import data as _seed_data

def main(argv):
    logging.basicConfig(level=getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO), stream=sys.stderr)
    suite = DataSuite()
    walker = DataWalker(suite)

    seed_data = dict(_seed_data.__dict__)
    seed_data['event_names'] = seed_data['event_names'][0:10]
    builder = FixtureBuilder(num_users=100, **seed_data)
    for organization_datum in [builder.build_organization_datum(code, name) for code, name in seed_data['organization_names']]:
        logging.info("Resolving references...")
        walker(organization_datum)

    for user_datum in builder.user_data:
        walker(user_datum)

    for service_datum in builder.service_data:
        walker(service_datum)

    for i in range(0, 4):
        walker(builder.build_api_key_datum('API%08d' % i))

    for site in builder.site_data:
        suite[site._tableau_schema].add(site)
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

    SQLGenerator(sys.stdout, encoding=getpreferredencoding())(suite)

if __name__ == '__main__':
    main(sys.argv)
