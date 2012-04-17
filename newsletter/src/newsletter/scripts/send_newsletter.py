import csv
import optparse
import os
import sys

from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message

from newsletter.newsletters.models import Newsletter, session

import logging
logging.basicConfig()

def main(argv=sys.argv):
    session.configure(autocommit=True, extension=[])

    parser = optparse.OptionParser(
        description=__doc__,
        usage='%prog [options]',
    )
    parser.add_option('-C', '--config',
        dest='config',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='FILE'
    )
    options, args = parser.parse_args(argv[1:])

    # configuration
    config = options.config
    if config is None:
        print 'You must give a config file'
        return
    app = loadapp('config:%s' % config, 'main')
    settings = app.registry.settings
    mailer = Mailer.from_settings(settings)

    # send mail magazine
    report = []
    for newsletter in Newsletter.get_reservations():
        if not newsletter.subscriber_file():
            report.append('id=%d: ERROR csv file not found. (%s)' % (newsletter.id, newsletter.subject[:40]))
            continue

        # update Newsletter.status to 'sending'
        newsletter.status = 'sending'
        Newsletter.update(newsletter)

        csv_file = os.path.join(Newsletter.subscriber_dir(), newsletter.subscriber_file())
        log_file = open(csv_file + '.log', 'w')
        count = {'sent':0, 'error':0} 
        for row in csv.DictReader(open(csv_file), Newsletter.csv_fields):
            result = newsletter.send(recipient=row['email'], name=row['name'])
            result = 'sent' if result else 'error'
            log_file.write('%s,%s\n' % (row['email'], result))
            count[result] += 1
        log_file.close()

        # update Newsletter.status to 'completed'
        newsletter.status = 'completed'
        Newsletter.update(newsletter)
        report.append('id=%d: sent=%d, error=%d (%s)' % (newsletter.id, count['sent'], count['error'], newsletter.subject[:40]))

    # report
    if report:
        message = Message(
            subject = 'mail magazine report',
            sender = settings['mail.report.sender'],
            recipients = [settings['mail.report.recipients']],
            body = '\n'.join(report)
        )
        mailer.send_immediately(message)

if __name__ == '__main__':
    main()

