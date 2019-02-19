import csv
import optparse
import os
import sys
import transaction

from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from pyramid.paster import bootstrap, setup_logging
from newsletter.newsletters.models import Newsletter, Mailer, session
from altair.multilock.lock import MultiStartLock

import logging

logger = logging.getLogger(__name__)

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
    setup_logging(config)
    env = bootstrap(config)
    request = env['request']
    settings = request.registry.settings


    with MultiStartLock(__name__):
        # send mail magazine
        report = []
        def do_report(msg):
            report.append(msg)
            logger.info(msg)
        for newsletter in Newsletter.get_reservations():
            if not newsletter.subscriber_file():
                do_report('id=%d: ERROR csv file not found. (%s)' % (newsletter.id, newsletter.subject[:40]))
                continue

            # update Newsletter.status to 'sending'
            newsletter.status = 'sending'
            Newsletter.update(newsletter)

            csv_file = os.path.join(Newsletter.subscriber_dir(), newsletter.subscriber_file())
            count = {'sent':0, 'error':0} 
            log_file = open(csv_file + '.log', 'w')
            try:
                for row in csv.DictReader(open(csv_file)):
                    result = newsletter.send(recipient=row['email'], settings=settings, **row)
                    result = 'sent' if result else 'error'
                    logger.info('%s: %s' % (row['email'], result)) 
                    log_file.write('%s,%s\n' % (row['email'], result))
                    count[result] += 1
            finally:
                log_file.close()

            # update Newsletter.status to 'completed'
            newsletter.status = 'completed'
            Newsletter.update(newsletter)
            do_report('id=%d: sent=%d, error=%d (%s)' % (newsletter.id, count['sent'], count['error'], newsletter.subject[:40]))

        # report
        if report:
            mailer = Mailer(settings)
            sender = settings['mail.report.sender']
            recipient = settings['mail.report.recipient']
            mailer.create_message(
                sender = sender,
                recipient = recipient,
                subject = 'mail magazine report',
                body = '\n'.join(report)
            )
            mailer.send(sender, recipient)

        transaction.commit()

if __name__ == '__main__':
    main()

