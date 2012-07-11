# encoding: utf-8
from ticketing.seed.fixtures import FixtureBuilder, STOCK_TYPE_TYPE_OTHER, STOCK_TYPE_TYPE_SEAT
from ticketing.seed.data import payment_method_names, delivery_method_names, payment_delivery_method_pair_matrix, bank_pairs, role_seeds, operator_seeds
from datetime import datetime
from itertools import chain
from pyramid.paster import bootstrap
from tableau import *
from tableau.sql import SQLGenerator
from tableau.sqla import newSADatum
import sqlahelper
import logging
import os
import sys
import transaction

class Bj89ersFixtureBuilder(FixtureBuilder):
    def __init__(self, Datum, **kwargs):
        FixtureBuilder.__init__(
            self,
            stock_type_triplets=[
                (u'会員権', STOCK_TYPE_TYPE_OTHER, True),
                (u'Tシャツ', STOCK_TYPE_TYPE_OTHER, True),
                ],
            stock_type_combinations={
                u'法人会員': [
                    (u'会員権', 100500),
                    (u'Tシャツ', 0),
                    ],
                u'プラチナ会員': [
                    (u'会員権', 30000),
                    (u'Tシャツ', 0),
                    ],
                u'ゴールド会員': [
                    (u'会員権', 10000),
                    (u'Tシャツ', 0),
                    ],
                u'レギュラー会員': [
                    (u'会員権', 3000),
                    ],
                u'ライト会員': [
                    (u'会員権', 1000),
                    ],
                u'ジュニア会員': [
                    (u'会員権', 1000),
                    ],
                },
                event_names=[
                    u"仙台89ers FC会員登録",
                    ],
                site_names=[
                    u"ダミー会場"
                    ],
                organization_names=[],
                account_pairs=[],
                performance_names=[
                    u"FC会員登録2012",
                    ],
                payment_method_names=payment_method_names,
                delivery_method_names=delivery_method_names,
                payment_delivery_method_pair_matrix=[
                    [ True, True, True ],
                    [ False, False, False ],
                    [ True, True, True ],
                    [ False, False, False ],
                    ],
                bank_pairs=bank_pairs,
                role_seeds=role_seeds,
                operator_seeds=operator_seeds,
                sales_segment_kind=['normal'],
                salt='bj89ers',
                num_users=1,
                Datum=Datum
                )
        self.organization_id = 12
        self.event_id = 42
        self.start_at = datetime(2012, 7, 1, 0, 0, 0)
        self.end_at = datetime(2012, 8, 31, 0, 0, 0)

    def build_event_datum(self, organization, title):
        stock_type_data = [
            self.build_stock_type_datum(_name, type, quantity_only)
            for _name, type, quantity_only in self.stock_type_triplets
            ]
        sales_segment_data = [
            self.build_sales_segment_datum(
                organization,
                u'会員登録',
                self.start_at,
                self.end_at
                ),
            ]
        account_datum = self.build_account_datum(u'仙台89ers', 2)
        stock_holder_data = [
            self.Datum(
                'StockHolder',
                name=u'仙台89ers',
                account=many_to_one(account_datum, 'account_id'),
                style='{}'
                )
            ]
        product_data = list(chain(*(
            self.build_product_data(sales_segment_datum) \
            for sales_segment_datum in sales_segment_data
            )))

        retval = self.Datum(
            'Event',
            id=self.event_id,
            title=title,
            organization=many_to_one(organization, 'organization_id'),
            stock_types=one_to_many(
                stock_type_data,
                'event_id'
                ),
            account=many_to_one(account_datum, 'account_id'),
            sales_segments=one_to_many(
                sales_segment_data,
                'event_id'
                ),
            stock_holders=one_to_many(
                stock_holder_data,
                'event_id'
                ),
            products=one_to_many(
                product_data,
                'event_id'
                )
            )
        retval.performances = one_to_many(
            [
                self.build_performance_datum(
                    organization, retval, name,
                    self.start_at) \
                for i, name in enumerate(self.performance_names)
                ],
            'event_id'
            )
        return retval

    def build(self):
        organization = self.build_organization_datum('89', u'仙台89ers')
        organization.id = self.organization_id
        return organization

if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO), stream=sys.stderr)
    if len(sys.argv) > 1:
        env = bootstrap(sys.argv[1])
        session = sqlahelper.get_session()
        import ticketing.core.models
        builder = Bj89ersFixtureBuilder(newSADatum(sqlahelper.get_base().metadata, sqlahelper.get_base()))
        session.add(builder.build())
        transaction.commit()
    else:
        builder = Bj89ersFixtureBuilder(Datum)
        suite = DataSuite() 
        walker = DataWalker(suite)
        walker(builder.build())
        for service_datum in builder.service_data:
            walker(service_datum)
        SQLGenerator(sys.stdout, encoding='utf-8')(suite)

