# -*- coding:utf-8 -*-

""" https://redmine.ticketstar.jp/issues/5265 対応用
あとで、console_scriptとして登録する
"""
import logging
import json
import argparse
from pyramid.paster import bootstrap, setup_logging
from altair.mq import get_publisher


logger = logging.getLogger(__name__)

class PublishLotElectingCommand(object):

    def __init__(self, request, work):
        self.request = request
        self.work = work

    @property
    def publisher(self):
        return get_publisher(self.request, 'lots')

    def run(self):
        publisher = self.publisher
        work = self.work
        logger.info("publish entry_wish = {0}-{1}".format(work.lot_entry_no, work.wish_order))
        body = {"lot_id": work.lot_id,
                "entry_no": work.lot_entry_no,
                "wish_order": work.wish_order,
        }
        print body
        publisher.publish(body=json.dumps(body),
                          routing_key="lots",
                          properties=dict(content_type="application/json"))
        print "end"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('lot_id')
    parser.add_argument('lot_entry_no')
    parser.add_argument('wish_order')

    args = parser.parse_args()
    setup_logging(args.config)
    env = bootstrap(args.config)

    request = env['request']

    cmd = PublishLotElectingCommand(request, args)
    cmd.run()


if __name__ == '__main__':
    main()
