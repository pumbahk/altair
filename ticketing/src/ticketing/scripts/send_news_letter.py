import csv
import optparse
import os
import sys
sys.path.append('/Users/mmatsui/Applications/altair-devel/altair/ticketing/src/ticketing')

from paste.deploy import loadapp
from pyramid.scripting import get_root
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message
from news_letters.models import NewsLetter

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

    for news_letter in NewsLetter.all():
        print 'news_letter:', vars(news_letter)
        recipients = csv.reader(open(news_letter.subscriber_file()))
        for row in recipients:
            id, name, email  = row
            if email is None: continue
            message = Message(
                subject = news_letter.subject,
                sender = "mmatsui@ticketstar.jp",
                recipients = [email],
                body = news_letter.description
            )
            print 'message:', vars(message)
            mailer.send_immediately(message)

if __name__ == '__main__':
    main()
