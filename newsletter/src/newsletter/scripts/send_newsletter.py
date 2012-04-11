import csv
import optparse
import os
import sys

from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp
from pyramid.scripting import get_root
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message

from newsletter.models import merge_session_with_post
from newsletter.newsletters.models import Newsletter

import logging
logging.basicConfig()

def main(argv=sys.argv):
    parser = optparse.OptionParser(
        description=__doc__,
        usage='%prog [options] [limit]',
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

        count = 0
        fields = ['id', 'name', 'email']
        for row in csv.DictReader(open(csv_file), fields):
            body = html = None
            if newsletter.type == 'html':
                html = newsletter.description.replace('${name}', row['name'])
            else:
                body = newsletter.description.replace('${name}', row['name'])

            message = Message(
                subject = newsletter.subject,
                sender = "mmatsui@ticketstar.jp",
                recipients = [row['email']],
                body = body,
                html = html,
            )
            print 'message:', vars(message)
            mailer.send_immediately(message)
            count += 1

        # update Newsletter.status to 'completed'
        record = merge_session_with_post(newsletter, {'status':'completed'})
        Newsletter.update(record)
        report['success'].append(str(count) + ':' + newsletter.subject)

    # report
    body = ''
    for key, subject in report.items():
        body += '# %s\n%s\n' % (key, '\n'.join(subject))

    message = Message(
        subject = 'mail magazine report',
        sender = "mmatsui@ticketstar.jp",
        recipients = ['mmatsui@ticketstar.jp'],
        body = body
    )
    print 'report:', vars(message)
    mailer.send_immediately(message)

if __name__ == '__main__':
    main()

