# -*- coding:utf-8 -*-

import argparse
import sys
import os
import logging
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from pyramid.paster import bootstrap, setup_logging
from altair.sqlahelper import get_global_db_session
import urllib2
from ..communication.preview import FamiPortTicketPreviewAPI

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    parser.add_argument('--image-type', metavar='image_type', type=str, dest='image_type', required=False, default='jpeg', choices=['jpeg', 'pdf'], help='image type')
    parser.add_argument('--endpoint', metavar='endpoint', type=str, dest='endpoint', required=False, help='endpoint')
    parser.add_argument('--user-name', metavar='user_name', type=str, dest='user_name', required=False, help='user name')
    parser.add_argument('--user-id', metavar='user_id', type=str, dest='user_id', required=False, help='member id')
    parser.add_argument('--user-address1', metavar='user_address1', type=str, dest='user_address1', required=False, help='address1')
    parser.add_argument('--user-address2', metavar='user_address2', type=str, dest='user_address2', required=False, help='address2')
    parser.add_argument('--user-identify-no', metavar='user_identify_no', type=str, dest='user_identify_no', required=False, help='identify_no')
    parser.add_argument('reserve_number', metavar='reserve_number', type=str, nargs='+', help='reserve number')
    args = parser.parse_args(argv[1:])

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    registry = env['registry']
    settings = registry.settings

    from ..models import FamiPortReceipt
    session = get_global_db_session(registry, 'famiport')

    preview_api = FamiPortTicketPreviewAPI(urllib2.build_opener(), args.endpoint or settings['altair.famiport.ticket_preview_api.endpoint_url'])

    for famiport_receipt in session.query(FamiPortReceipt).filter(FamiPortReceipt.reserve_number.in_(args.reserve_number)).all():
        images = preview_api(
            request,
            discrimination_code=unicode(famiport_receipt.famiport_order.famiport_client.playguide.discrimination_code_2),
            client_code=famiport_receipt.famiport_order.famiport_client.code,
            order_id=famiport_receipt.famiport_order_identifier,
            barcode_no=famiport_receipt.barcode_no,
            name=args.user_name,
            member_id=args.user_id,
            address_1=args.user_address1,
            address_2=args.user_address2,
            identify_no=args.user_identify_no,
            tickets=[
                dict(
                    barcode_no=famiport_ticket.barcode_number,
                    template_code=famiport_ticket.template_code,
                    data=famiport_ticket.data
                    )
                for famiport_ticket in famiport_receipt.famiport_order.famiport_tickets
                ],
            response_image_type=args.image_type
            )
        for i, image in enumerate(images):
            path = '%(reserve_number)s_%(serial)02d.%(ext)s' % dict(reserve_number=famiport_receipt.reserve_number, serial=i, ext=args.image_type)
            logger.info('saving image to %s' % path)
            with open(path, 'w') as f:
                f.write(image)
    
if __name__ == u"__main__":
    main(sys.argv)



