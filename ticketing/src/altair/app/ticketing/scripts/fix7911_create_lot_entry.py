#-*- coding: utf-8 -*-
#!/usr/bin/env python
import argparse
import csv
import sys
from datetime import date

import transaction
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core.models import DBSession, Organization, PaymentDeliveryMethodPair
from altair.app.ticketing.lots import api, helpers
from altair.app.ticketing.lots.models import Lot
from pyramid.paster import bootstrap

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('--file_name', metavar='file_name', type=str, required=True)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']

    transaction.begin()
    with open(args.file_name, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header

        for row in reader:
            org_id = row[0]
            lot_id = row[1]
            payment_delivery_method_pair_id = row[2]
            product_id = row[3]
            quantity = row[4]
            birth_year = int(row[5])
            birth_month = int(row[6])
            birth_day = int(row[7])
            zip = row[8] # ハイフンなし
            prefecture = row[9]
            city = row[10]
            address = row[11]
            tel = row[12]
            email = row[13]
            last_name = row[14]
            last_name_kana = row[15]
            first_name = row[16]
            first_name_kana = row[17]

            # get shipping_address
            birthday = date(birth_year, birth_month, birth_day)
            shipping_address_dict = {'last_name_kana': last_name_kana, 'fax': u'', 'last_name': last_name, 'sex': u'2',
                                     'birthday': birthday, 'prefecture': prefecture,
                                     'city': city, 'first_name': first_name, 'zip': zip, 'tel_2': u'', 'tel_1': tel,
                                     'email_1': email, 'address_1': address, 'address_2': u'', 'country': u'日本',
                                     'first_name_kana': first_name_kana}
            shipping_address = helpers.convert_shipping_address(shipping_address_dict)
            shipping_address.user = None

            payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter_by(id=payment_delivery_method_pair_id).first()

            # get entry_no
            org = Organization.query.filter(Organization.id == org_id).first()
            entry_no = api.generate_entry_no(request, org)
            #get wishes
            lot = Lot.query.filter(Lot.id == lot_id).first()
            performances = lot.performances
            wishes = [{'performance_id': unicode(performances[0].id),
                       'wished_products': [{'wish_order': 0, 'product_id': unicode(product_id), 'quantity': quantity}]}]
            #create info
            info = {'organization_id': org_id, 'is_guest': True, 'membership': None, 'membership_source': None}

            entry = api.build_lot_entry(
                lot=lot,
                wishes=wishes,
                membergroup=cart_api.get_member_group(request, info),
                membership=cart_api.get_membership(info),
                payment_delivery_method_pair=payment_delivery_method_pair,
                shipping_address=shipping_address,
                user=None,
                gender=(u'2',),
                birthday=birthday,
                memo=u'',
                channel= 3 # インナー
                )

            for wish in entry.wishes:
                wish.entry_wish_no = "{0}-{1}".format(entry_no, wish.wish_order)
            entry.browserid = ''
            entry.user_agent = ''
            entry.cart_session_id = ''
            entry.user_point_accounts = []
            entry.entry_no = entry_no
            print ("entry_no:",entry.entry_no)

            DBSession.add(entry)
            DBSession.flush()
    transaction.commit()

if __name__ == '__main__':
    main()
