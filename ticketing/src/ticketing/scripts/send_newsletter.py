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
from ticketing.models import merge_session_with_post

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

    # configuration
    config = options.config
    print 'options:', options
    if config is None:
        return
    app = loadapp('config:%s' % config, 'main')

    mailer = Mailer()
    print 'mailer:', vars(mailer.smtp_mailer)

    # send mail magazine
    report = {'success':[], 'fail':[]}
    for newsletter in Newsletter.get_reservations():
        print 'newsletter:', vars(newsletter)
        csv_file = os.path.join(Newsletter.subscriber_dir(), newsletter.subscriber_file())
        if not os.path.exists(csv_file):
            report['fail'].append(newsletter.subject)
            continue

        recipients = csv.reader(open(csv_file))
        for row in recipients:
            id, name, email  = row
            if email is None: continue
            message = Message(
                subject = newsletter.subject,
                sender = "mmatsui@ticketstar.jp",
                recipients = [email],
                body = newsletter.description.replace('${name}', name)
            )
            print 'message:', vars(message)
            mailer.send_immediately(message)

        # update Newsletter.status to 'completed'
        record = merge_session_with_post(newsletter, {'status':'completed'})
        Newsletter.update(record)
        report['success'].append(newsletter.subject)

    # report
    body = ''
    for key, subject in report.items():
        body += '# %s\n%s\n' % (key, '\n'.join(subject))

    message = Message(
        subject = 'mail magazine send report',
        sender = "mmatsui@ticketstar.jp",
        recipients = ['mmatsui@ticketstar.jp'],
        body = body
    )
    mailer.send_immediately(message)

if __name__ == '__main__':
    main()
