# -*- coding:utf-8 -*-
import sys
import argparse
from pyramid.paster import bootstrap, setup_logging
from ..reporting import send_lot_report_mails


class SendLotReportMailsCommand(object):
    def __init__(self, request):
        self.request = request
        settings = request.registry.settings
        self.sender = settings['mail.message.sender']

    def run(self):
        send_lot_report_mails(self.request,
                              self.sender)


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument("config")

    args = parser.parse_args(args)

    setup_logging(args.config)
    env = bootstrap(args.config)

    request = env['request']

    cmd = SendLotReportMailsCommand(request)
    cmd.run()

if __name__ == '__main__':
    main()
