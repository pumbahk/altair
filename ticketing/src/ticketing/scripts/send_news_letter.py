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
    parser.add_option('-C', '--config', dest='config',
        help='Path to configuration file (defaults to $CWD/etc/hoge.ini)',
        metavar='FILE')
    parser.add_option('-f', '--filter', dest='filter', action='store_true',
        help='Limit results to users specified by username in stdin.  Users'
             ' should be whitespace delimited.', default=False)
    options, args = parser.parse_args(argv[1:])

    config = options.config
    print options, config
    if config is None:
        return
    app = loadapp('config:%s' % config, 'main')

    mailer = Mailer()
    print vars(mailer.smtp_mailer)

    for news_letter in NewsLetter.all():
        recipients = csv.reader(open(news_letter.subscriber_file()))
        print recipients
        for row in recipients:
            id, email  = row
            message = Message(subject="hello",
                sender="mmatsui@ticketstar.jp",
                recipients=[row[1]],
                body="hello test")
            print vars(message)
            #mailer.send_immediately(message)


    """
    if not args:
        parser.error('Please specify queue path.')
    elif len(args) > 1:
        parser.error('Too many arguments.')
    queue_path = args[0]

    config = options.config
    if config is None:
        config = get_default_config()
    app = loadapp('config:%s' % config, 'karl')
    set_subsystem('mailout')

    mailer = SMTPMailer(
        hostname=options.hostname,
        port=options.port,
        username=options.username,
        password=options.password,
        no_tls=options.no_tls,
        force_tls=options.force_tls
    )   
    qp = QueueProcessor(mailer, queue_path)

    if options.daemon:
        run_daemon('digest', qp.send_messages, options.interval)
    else:
        qp.send_messages()
    """

if __name__ == '__main__':
    main()

