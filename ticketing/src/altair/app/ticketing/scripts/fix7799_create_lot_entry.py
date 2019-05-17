#-*- coding: utf-8 -*-
#!/usr/bin/env python
import argparse
import csv
import sys
from datetime import date

import transaction
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart.view_support import coerce_extra_form_data
from altair.app.ticketing.core.models import DBSession, Organization, PaymentDeliveryMethodPair
from altair.app.ticketing.lots import api
from altair.app.ticketing.lots import helpers as h
from altair.app.ticketing.lots.models import Lot
from pyramid.paster import bootstrap


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('--file_name', metavar='file_name', type=str, required=True)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']
    import sys
    print(sys.version)
    with open(args.file_name, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header

        for row in reader:
            org_id = row[0]
            lot_id = row[1]
            payment_delivery_method_pair_id = row[2]
            product_id = row[3]  # A2958020, B2958886, C2958889, D2958891, E2958897, ローカルは、A146, B148, C150, D152, E154
            quantity = row[4]
            extra = {row[5]: row[6]}
            birth_year = int(row[7])
            birth_month = int(row[8])
            birth_day = int(row[9])
            zip = row[10] # ハイフンなし
            prefecture = row[11]
            city = row[12]
            address = row[13]
            tel = row[14]
            email = row[15]
            last_name = row[16]
            last_name_kana = row[17]
            first_name = row[18]
            first_name_kana = row[19]

            channel = 3 # インナー
            user_point_accounts = []
            review_password = None
            org = Organization.query.filter(Organization.id == org_id).first()  # 本番は155、ローカルは32
            lot = Lot.query.filter(Lot.id == lot_id).first()
            performances = lot.performances
            wishes = [{'performance_id': unicode(performances[0].id),
                       'wished_products': [{'wish_order': 0, 'product_id': unicode(product_id), 'quantity': quantity}]}]
            payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter_by(id=payment_delivery_method_pair_id).first()
            payment_delivery_method_pair
            birthday = date(birth_year, birth_month, birth_day)

            gender = (u'2',)
            memo = u''
            orion_ticket_phone = u''

            shipping_address_dict = {'last_name_kana': last_name_kana, 'fax': u'', 'last_name': last_name, 'sex': u'2',
                                     'birthday': birthday, 'prefecture': prefecture,
                                     'city': city, 'first_name': first_name, 'zip': zip, 'tel_2': u'', 'tel_1': tel,
                                     'email_1': email, 'address_1': address, 'address_2': u'', 'country': u'日本',
                                     'first_name_kana': first_name_kana}

            entry_no = api.generate_entry_no(request, org)

            entry = {
                'payment_delivery_method_pair_id': unicode(payment_delivery_method_pair.id),
                'extra': extra,
                'gender': gender,
                'memo': u'',
                'birthday': date(birth_year, birth_month, birth_day),
                'wishes': wishes,
                'shipping_address': shipping_address_dict,
                'lot_id': lot_id,
                'review_password': review_password,
                'orion_ticket_phone': orion_ticket_phone,
                'entry_no': entry_no
            }

            entry_no = entry['entry_no']
            shipping_address = entry['shipping_address']
            shipping_address = h.convert_shipping_address(shipping_address)
            user = None
            shipping_address.user = user
            wishes = entry['wishes']
            orion_ticket_phone = None

            info = {'organization_id': org_id, 'is_guest': True, 'membership': None, 'membership_source': None}
            entry = api.build_lot_entry(
                lot=lot,
                wishes=wishes,
                membergroup=cart_api.get_member_group(request, info),
                membership=cart_api.get_membership(info),
                payment_delivery_method_pair=payment_delivery_method_pair,
                shipping_address=shipping_address,
                user=user,
                gender=gender,
                birthday=birthday,
                memo=memo,
                channel=channel
                )
            entry.browserid = ''
            entry.user_agent = ''
            entry.cart_session_id = ''
            entry.user_point_accounts = user_point_accounts

            if extra:
                entry.attributes = coerce_extra_form_data(request, extra)

            entry.entry_no = entry_no
            DBSession.add(entry)
            if orion_ticket_phone:
                DBSession.add(orion_ticket_phone)
            DBSession.flush()

            for wish in entry.wishes:
                wish.entry_wish_no = "{0}-{1}".format(entry.entry_no, wish.wish_order)

    transaction.commit()


if __name__ == '__main__':
    main()
