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

import ConfigParser
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
    if config is None:
        return
    app = loadapp('config:%s' % config, 'main')

    # mailer setup
    parser = ConfigParser.SafeConfigParser()
    parser.read(config)
    settings = dict(parser.items('mailer'))
    mailer = Mailer.from_settings(settings)

    # send mail magazine
    report = {'success':[], 'fail':[]}
    for newsletter in Newsletter.get_reservations():

        csv_file = os.path.join(Newsletter.subscriber_dir(), newsletter.subscriber_file())
        if not os.path.exists(csv_file):
            report['fail'].append(newsletter.subject)
            continue

        # update Newsletter.status to 'sending'
        record = merge_session_with_post(newsletter, {'status':'sending'})
        Newsletter.update(record)

        count = 0
        fields = ['id', 'name', 'email']
        for row in csv.DictReader(open(csv_file), fields):
            body = html = None
            if newsletter.type == 'html':
                html = newsletter.description.replace('${name}', row['name'])
            else:
                body = newsletter.description.replace('${name}', row['name'])

            message = Message(
                sender = settings['message.sender'],
                subject = newsletter.subject,
                recipients = [row['email']],
                body = body,
                html = html,
            )
            mailer.send_immediately(message)
            count += 1

        # update Newsletter.status to 'completed'
        record = merge_session_with_post(newsletter, {'status':'completed'})
        Newsletter.update(record)
        report['success'].append(str(count) + ':' + newsletter.subject)

    # report
    body = ''
    for key, subject in report.items():
        body += '[%s]\n%s\n' % (key, '\n'.join(subject))

    if report['success'] or report['fail']:
        message = Message(
            subject = 'mail magazine report',
            sender = settings['report.sender'],
            recipients = [settings['report.recipients']],
            body = body
        )
        mailer.send_immediately(message)

if __name__ == '__main__':
    main()

