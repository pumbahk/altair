import os
import sys
from locale import getpreferredencoding
from fixtures import sites, organization_names, build_organization_datum, build_user_datum, build_mail_magazines, build_user_datum, service_data
from tableau import DataSuite, DataWalker
from tableau.sql import SQLGenerator
from svggen import SVGGenerator, NESW
from lxml.etree import tostring
import logging
from cProfile import run

def main(argv):
    logging.basicConfig(level=getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO), stream=sys.stderr)
    suite = DataSuite()
    walker = DataWalker(suite)

    user_data = [build_user_datum() for _ in range(100)]
    for organization_datum in [build_organization_datum(user_data, code, name) for code, name in organization_names]:
        organization_datum.user_id=build_user_datum()
        mail_magazines = build_mail_magazines(organization_datum)
        logging.info("Resolving references...")
        walker(organization_datum)
        for mail_magazine in mail_magazines:
            walker(mail_magazine)

    for user_datum in user_data:
        walker(user_datum)

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

    SQLGenerator(sys.stdout, encoding=getpreferredencoding())(suite)

if __name__ == '__main__':
    main(sys.argv)
