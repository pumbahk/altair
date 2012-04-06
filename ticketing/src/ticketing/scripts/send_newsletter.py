import csv
import optparse
import os
import sys
sys.path.append('/Users/mmatsui/Applications/altair-devel/altair/ticketing/src/ticketing')

from paste.deploy import loadapp
from pyramid.scripting import get_root
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message
from newsletters.models import Newsletter

import logging
logging.basicConfig()

def main(argv=sys.argv):
    parser = optparse.OptionParser(
        description=__doc__,
        usage="%prog [options] [limit]",
    )
    parser.add_option('-C', '--config',
        dest='config',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='FILE'
    )
    options, args = parser.parse_args(argv[1:])

    config = options.config
    print 'options:', options
    if config is None:
        return
    app = loadapp('config:%s' % config, 'main')

    mailer = Mailer()
    print 'mailer:', vars(mailer.smtp_mailer)

    for newsletter in Newsletter.all():
        print 'newsletter:', vars(newsletter)
        recipients = csv.reader(open(newsletter.subscriber_file()))
        for row in recipients:
            id, name, email  = row
            if email is None: continue
            message = Message(
                subject = newsletter.subject,
                sender = "mmatsui@ticketstar.jp",
                recipients = [email],
                body = newsletter.description
            )
            print 'message:', vars(message)
            mailer.send_immediately(message)

if __name__ == '__main__':
    main()
