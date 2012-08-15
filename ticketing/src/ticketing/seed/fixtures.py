# encoding: utf-8

from random import randint, choice, sample, shuffle
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from itertools import chain
from ticketing.core.models import SeatStatusEnum
from tableau import many_to_many, one_to_many, many_to_one, auto, Datum
from collections import OrderedDict
import logging
import hashlib
import json

__all__ = (
    'STOCK_TYPE_TYPE_SEAT',
    'STOCK_TYPE_TYPE_OTHER',
    'FixtureBuilder',
    )

logger = logging.getLogger('fixtures')

STOCK_TYPE_TYPE_SEAT = 0
STOCK_TYPE_TYPE_OTHER = 1

class NotEnoughStockError(Exception):
    pass

class DigitCodec(object):
    def __init__(self, digits):
        self.digits = digits

    def encode(self, num):
        l = len(self.digits)
        retval = []
        n = num
        while True:
            rem = n % l
            quo = n // l
            retval.insert(0, self.digits[rem])
            if quo == 0:
                break
            n = quo
        return ''.join(retval)

    def decode(self, s):
        i = 0
        sl = len(s)
        l = len(self.digits)
        retval = 0
        while i < sl:
            c = s[i]
            d = self.digits.find(c)
            if d < 0:
                raise ValueError("Invalid digit: " + c)
            retval *= l
            retval += d
            i += 1
        return retval

encoder = DigitCodec("0123456789ACFGHJKLPRSUWXYZ")
sensible_alnum_encode = encoder.encode
sensible_alnum_decode = encoder.decode

def permute(iterable):
    retval = list(iterable)
    shuffle(retval)
    return retval

def random_date():
    return datetime.now().date().replace(month=1, day=1) + relativedelta(days=randint(0, 364))

def some_day_between(start, end):
    return start + relativedelta(days=randint(0, (end - start).days))

def random_color():
    return u'#%x%x%x' % (randint(0, 15), randint(0, 15), randint(0, 15))

def random_order_number(organization):
    return organization.code + sensible_alnum_encode(randint(0, 10000000)).zfill(10)

class FixtureBuilder(object):
    def __init__(self, stock_type_triplets,
            stock_type_combinations, event_names, site_names,
            organization_names, account_pairs,
            performance_names, payment_method_names, delivery_method_names,
            payment_delivery_method_pair_matrix, bank_pairs, role_seeds,
            operator_seeds, sales_segment_kind, salt, num_users,
            Datum=Datum, **kwargs):
        self.stock_type_triplets = stock_type_triplets
        self.stock_type_combinations = stock_type_combinations
        self.event_names = event_names
        self.site_names = site_names
        self.organization_names = organization_names
        self.account_pairs = account_pairs
        self.performance_names = performance_names
        self.payment_method_names = payment_method_names
        self.delivery_method_names = delivery_method_names
        self.payment_delivery_method_pair_matrix = payment_delivery_method_pair_matrix
        self.bank_pairs = bank_pairs
        self.role_seeds = role_seeds
        self.operator_seeds = operator_seeds
        self.sales_segment_kind = sales_segment_kind
        self.salt = salt
        self.num_users = num_users
        class _Datum(Datum):
            def __init__(self, schema, **fields):
                Datum.__init__(self, schema, auto('id'), **fields)
        self.Datum = _Datum
        self._Datum = Datum

    def singleton(func):
        cell = [None]
        def accessor(self):
            if cell[0] is None:
                cell[0] = func(self)
            return cell[0]
        return property(accessor)

    def build_user_data(self):
        return [self.build_user_datum() for _ in range(self.num_users)]

    user_data = singleton(build_user_data)

    def build_site_data(self):
        return [self.build_site_datum(name) for name in self.site_names]

    site_data = singleton(build_site_data)

    def build_bank_data(self):
        return [
            self.Datum(
                'Bank',
                code=code,
                name=name
                ) \
            for code, name in self.bank_pairs
            ]

    bank_data = singleton(build_bank_data)

    def build_payment_method_plugin_data(self):
        return [
            self.Datum(
                'PaymentMethodPlugin',
                name=name
                ) \
            for name in self.payment_method_names
            ]

    payment_method_plugin_data = singleton(build_payment_method_plugin_data)

    def build_delivery_method_data(self):
        return [
            self.Datum(
                'DeliveryMethodPlugin',
                name=name
                ) \
            for name in self.delivery_method_names
            ]

    delivery_method_plugin_data = singleton(build_delivery_method_data)

    def build_operator_role_map(self):
        return dict(
            (
                name,
                self.Datum(
                    'OperatorRole',
                    name=name,
                    permissions=one_to_many(
                        [self.Datum(
                            'Permission',
                            category_name=category_name,
                            permit=permit
                            ) \
                        for category_name, permit in permissions
                        ],
                        'operator_role_id'
                        ),
                    status=1
                    )
                ) \
            for name, permissions in self.role_seeds.iteritems()
            )

    operator_role_map = singleton(build_operator_role_map)

    def build_service_data(self):
        return [
            self.Datum(
                'Service',
                name=u'Altair CMS',
                key=u'fa12a58972626f0597c2faee1454e1',
                secret=u'c5f20843c65870fad8550e3ad1f868',
                redirect_uri=u'http://127.0.0.1:6543/auth/oauth_callback'
                )
            ]

    service_data = singleton(build_service_data)

    def build_site_datum(self, name):
        colgroups = ['0'] + ['ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i] for i, (_, type, quantity_only) in enumerate(self.stock_type_triplets) if type == STOCK_TYPE_TYPE_SEAT and not quantity_only]
        return self.Datum(
            'Site',
            name=name,
            drawing_url=lambda self:'file:src/ticketing/static/site-data/%08d.xml' % self._id[0],
            _config=dict(
                colgroups=[
                    (colgroup, u'colgroup-%s' % colgroup, [u'%s-%d' % (colgroup, i + 1) for i in range(0, randint(1, 50) * 10)]) \
                    for colgroup in colgroups
                    ],
                seats_per_row=10
                )
            )

    def build_payment_method_datum(self, organization, payment_method_plugin):
        return self.Datum(
            'PaymentMethod',
            name=payment_method_plugin.name,
            fee=randint(1, 4) * 100,
            fee_type=randint(0, 1),
            organization=many_to_one(organization, 'organization_id'),
            payment_plugin=many_to_one(payment_method_plugin, 'payment_plugin_id')
            )

    def build_delivery_method_datum(self, organization, delivery_method_plugin):
        return self.Datum(
            'DeliveryMethod',
            name=delivery_method_plugin.name,
            fee=randint(1, 4) * 100,
            fee_type=randint(0, 1),
            organization=many_to_one(organization, 'organization_id'),
            delivery_plugin=many_to_one(delivery_method_plugin, 'delivery_plugin_id')
            )

    def build_account_datum(self, name, type):
        return self.Datum(
            'Account',
            name=name,
            account_type=type,
            user=many_to_one(self.build_user_datum(), 'user_id')
            )

    def build_seat_datum(self, group_l0_id, l0_id, stock, name):
        return self.Datum(
            'Seat',
            name=name,
            l0_id=l0_id,
            stock=many_to_one(stock, 'stock_id'),
            venue_id=None,
            group_l0_id=group_l0_id,
            venue_areas=many_to_many(
                [],
                ('venue_id', 'group_l0_id'),
                'venue_area_id',
                'VenueArea_group_l0_id'
                ),
            status_=one_to_many(
                [self._Datum(
                    'SeatStatus',
                    'seat_id',
                    status=SeatStatusEnum.Vacant.v
                    )],
                'seat_id'
                )
            )

    def build_seat_index_type_data(self, seats):
        return [
            self.Datum(
                'SeatIndexType',
                name=u'前から',
                seat_indexes=one_to_many(
                    [
                        self._Datum(
                            'SeatIndex',
                            ('seat_index_type_id', 'seat_id'),
                            seat_id=seat,
                            index=i
                            )
                            for i, seat in zip(range(1, len(seats) + 1), seats)
                        ],
                    'seat_index_type_id'
                    )
                ),
            self.Datum(
                'SeatIndexType',
                name=u'ランダム',
                seat_indexes=one_to_many(
                    [
                        self._Datum(
                            'SeatIndex',
                            ('seat_index_type_id', 'seat_id'),
                            seat_id=seat,
                            index=i
                            )
                        for i, seat in zip(permute(range(1, len(seats) + 1)), seats)
                        ],
                    'seat_index_type_id'
                    )
                ),
            ]

    def build_venue_area_datum(self, venue, colgroup):
        return self.Datum(
            'VenueArea',
            name=colgroup[0],
            groups=one_to_many(
                [self._Datum(
                    'VenueArea_group_l0_id',
                    ('venue_id', 'group_l0_id', 'venue_area_id'),
                    venue_id=venue,
                    group_l0_id=colgroup[1]
                    )],
                'venue_area_id'
                )
            )

    def build_adjacency_set_datum(self, l0_id_to_seat, config, n):
        seats_per_row = config['seats_per_row']
        adjacency_data = []
        for _, _, seat_ids in config['colgroups']:
            for row_num in range(0, len(seat_ids), seats_per_row):
                seats_in_row = [
                    l0_id_to_seat[l0_id] \
                    for l0_id in seat_ids[row_num:row_num + seats_per_row]
                    ]
                for i in range(0, seats_per_row - n + 1):
                    adjacency_data.append(self.Datum(
                        'SeatAdjacency',
                        seats=many_to_many(
                            seats_in_row[i:i+n],
                            'seat_adjacency_id',
                            'seat_id',
                            'Seat_SeatAdjacency',
                            )
                        ))
        return self.Datum(
            'SeatAdjacencySet',
            seat_count=n,
            adjacencies=one_to_many(
                adjacency_data,
                'adjacency_set_id'
                )
            )

    def build_venue_datum(self, organization, site, stock_sets):
        logger.info(u"Building Venue %s" % site.name)
        config = site._config
        seats = []
        l0_id_to_seat = {}
        for i, stocks in stock_sets:
            colgroup = config['colgroups'][i]
            seat_index = 0
            for stock in stocks:
                for i, l0_id in enumerate(colgroup[2][seat_index:seat_index + stock.quantity]):
                    seat_datum = self.build_seat_datum(colgroup[1], l0_id, stock, u'ブロック%s %s番' % (colgroup[0], i + 1))
                    seats.append(seat_datum)
                    l0_id_to_seat[l0_id] = seat_datum
                seat_index += stock.quantity

        adjacency_set_data = [
            self.build_adjacency_set_datum(l0_id_to_seat, config, n) \
            for n in range(2, config['seats_per_row'])
            ]

        retval = self.Datum(
            'Venue',
            name=site.name,
            seats=one_to_many(
                seats,
                'venue_id'
                ),
            site=many_to_one(site, 'site_id'),
            organization=many_to_one(organization, 'organization_id'),
            adjacency_sets=one_to_many(
                adjacency_set_data,
                'venue_id'
                ),
            seat_index_types=one_to_many(
                self.build_seat_index_type_data(seats),
                'venue_id'
                )
            )
        retval.areas = many_to_many(
            [
                self.build_venue_area_datum(retval, config['colgroups'][i]) \
                for i, _ in stock_sets
                ],
            'venue_id',
            'venue_area_id'
            )
        return retval

    def build_bank_account_datum(self):
        return self.Datum(
            'BankAccount',
            bank=many_to_one(choice(self.bank_data), 'bank_id'),
            account_type=1,
            account_number=u''.join(choice(u'0123456789') for _ in range(0, 7)),
            account_owner=u'ラクテン タロウ'
            )

    def build_mail_magazine(self, name, organization):
        return self.Datum(
            'MailMagazine',
            name=name,
            description=u"""<span class="mailMagazineFrequency">月曜日配信</span><span class="mailMagazineDescription">旬なエンタメ情報とエンタメに関する商品情報をお届けします！</span>""",
            organization=many_to_one(organization, 'organization_id'),
            )

    def build_mail_magazines(self, organization):
        return [
            self.build_mail_magazine(u"%s%sメルマガZ" % (organization.name, adjective), organization)
            for adjective in [u'わくわく', u'とくとく', u'ドキドキ']
            ]

    def build_user_datum(self):
        return self.Datum(
            'User',
            bank_account=many_to_one(self.build_bank_account_datum(), 'bank_account_id'),
            user_profile=one_to_many(
                [self.Datum(
                    'UserProfile',
                    email=lambda self: "dev+test%03d@ticketstar.jp" % self._id[0],
                    nick_name=lambda self: "dev+test%03d@ticketstar.jp" % self._id[0],
                    first_name=lambda self: u"太郎%d" % self._id[0],
                    last_name=u"楽天",
                    first_name_kana=u"タロウ",
                    last_name_kana=u"ラクテン",
                    birth_day=date(randint(1930, 2000), randint(1, 12), 1) + relativedelta(days=randint(0, 30)),
                    sex=1,
                    zip="251-0036",
                    prefecture=u"東京都",
                    city=u"品川区",
                    address_1=u"東五反田5-21-15'",
                    address_2=u"メタリオンOSビル",
                    tel_1=u"03-9999-9999",
                    tel_2=u"090-0000-0000",
                    fax=u"03-9876-5432"
                    )],
                'user_id'
                )
            )

    def build_operator_datum(self, name, operator_roles):
        return self.Datum(
            'Operator',
            name=name,
            email=lambda self: 'dev+test%03d@ticketstar.jp' % self._id[0],
            roles=many_to_many(
                operator_roles,
                'operator_id',
                'operator_role_id',
                'OperatorRole_Operator'
                ),
            expire_at=None,
            status=1,
            auth=one_to_many([
                self._Datum(
                    'OperatorAuth',
                    'operator_id',
                    login_id=lambda self: u'dev+test%03d@ticketstar.jp' % self._id[0] if self._id[0] > 1 else u'admin',
                    password=hashlib.md5('admin').hexdigest(),
                    auth_code=u'auth_code',
                    access_token=u'access_token',
                    secret_key=u'secret_key'
                    )],
                'operator_id'
                )
            )

    def build_api_key_datum(self, apikey):
        return self.Datum(
            'APIKey',
            expire_at=None,
            apikey=apikey
            )

    def gendigest(self, password):
        return hashlib.sha1(self.salt + password).hexdigest()

    def build_user_credential(self, user):
        return self.Datum(
            'UserCredential',
            auth_identifier=user.email,
            auth_secret=gendigest("asdfasdf")
            )

    def build_organization_datum(self, code, name):
        logger.info(u"Building Organization %s" % name)
        account_data = [
            self.build_account_datum(name_, type) \
            for name_, type in self.account_pairs
            ]
        retval = self.Datum(
            'Organization',
            name=name,
            code=code,
            accounts=one_to_many(account_data, 'organization_id'),
            operators=one_to_many(
                [
                    self.build_operator_datum(
                        operator_name,
                        [self.operator_role_map[role_name] \
                         for role_name in role_names]
                        ) \
                    for operator_name, role_names in self.operator_seeds.iteritems()
                    ],
                'organization_id',
                ),
            user=many_to_one(
                [
                    account_datum.user \
                    for account_datum in account_data \
                    if account_datum.name == name
                    ][0],
                'user_id'
                )
            )
        payment_method_data = [
            self.build_payment_method_datum(
                retval,
                payment_method_plugin_datum) \
            for payment_method_plugin_datum in self.payment_method_plugin_data
            ]
        delivery_method_data = [
            self.build_delivery_method_datum(
                retval,
                delivery_method_plugin_datum) \
            for delivery_method_plugin_datum in self.delivery_method_plugin_data
            ]
        retval.payment_method_list = one_to_many(
            payment_method_data,
            'organization_id'
            )
        retval.delivery_method_list = one_to_many(
            delivery_method_data,
            'organization_id'
            )
        event_data = [
            self.build_event_datum(retval, name) \
            for name in self.event_names
            ]
        retval.events = one_to_many(
            event_data,
            'organization_id'
            )
        retval.mail_magazines = one_to_many(
            self.build_mail_magazines(retval),
            'organization_id'
            )
        return retval

    def build_sales_segment_datum(self, organization, name, start_at, end_at):
        dayrange = min((end_at - start_at).days, 7)
        payment_delivery_method_pairs = [
            self.Datum(
                'PaymentDeliveryMethodPair',
                system_fee=randint(1, 2) * 100,
                transaction_fee=randint(1, 4) * 100,
                delivery_fee=randint(1, 4) * 100,
                discount=randint(0, 40) * 10,
                discount_unit=randint(0, 1),
                payment_method=many_to_one(organization.payment_method_list[payment_method_index], 'payment_method_id'),
                delivery_method=many_to_one(organization.delivery_method_list[delivery_method_index], 'delivery_method_id'),
                payment_period_days=randint(2, 4),
                issuing_interval_days=dayrange,
                issuing_start_at=start_at + relativedelta(days=randint(0, dayrange)),
                issuing_end_at=end_at - relativedelta(days=randint(0, dayrange)),
                ) \
            for payment_method_index, row in enumerate(self.payment_delivery_method_pair_matrix) \
            for delivery_method_index, enabled in enumerate(row) if enabled
            ]

        return self.Datum(
            'SalesSegment',
            name=name,
            start_at=start_at,
            end_at=end_at,
            upper_limit=randint(1, 10),
            seat_choice=randint(0, 1) != 0,
            kind=self.sales_segment_kind[randint(0, len(self.sales_segment_kind) - 1)],
            payment_delivery_method_pairs=one_to_many(
                payment_delivery_method_pairs,
                'sales_segment_id'
                )
            )

    def build_stock_datum(self, performance, stock_type, stock_holder, quantity):
        return self.Datum(
            'Stock',
            performance=many_to_one(performance, 'performance_id'),
            stock_type=many_to_one(stock_type, 'stock_type_id'),
            quantity=quantity,
            stock_holder=many_to_one(stock_holder, 'stock_holder_id'),
            stock_status=one_to_many(
                [self._Datum(
                    'StockStatus',
                    'stock_id',
                    quantity=quantity,
                    )],
                'stock_id'
                )
            )

    def build_performance_datum(self, organization, event, name, performance_date, build_venue=True):
        logger.info(u"Building Performance %s" % name)

        retval = self.Datum(
            'Performance',
            name=name,
            open_on=datetime.combine(performance_date, time(18, 0, 0)),
            start_on=datetime.combine(performance_date, time(19, 0, 0)),
            end_on=datetime.combine(performance_date, time(21, 0, 0))
            )
        if build_venue:
            site = choice(self.site_data)
        else:
            site = None
        stock_data = []
        stock_sets = []
        if site is not None:
            # unassigned seats
            stock_sets.append(
                (0, [self.build_stock_datum(retval, None, None, len(site._config['colgroups'][0][2]))])
                )
        colgroup_index = 1 # first colgroup is for "unassigned" seats.
        for stock_type in event.stock_types:
            stock_set = []
            if stock_type.type == STOCK_TYPE_TYPE_SEAT and not stock_type.quantity_only:
                colgroup = site._config['colgroups'][colgroup_index]
                quantity = len(colgroup[2])
                stock_sets.append((colgroup_index, stock_set))
                colgroup_index += 1
            else:
                quantity = randint(10, 100) * 10
            rest = quantity
            for i, stock_holder in enumerate(chain([None], event.stock_holders)):
                assigned = rest if i == len(event.stock_holders) - 1 else randint(0, rest)
                stock_datum = self.build_stock_datum(retval, stock_type, stock_holder, assigned)
                stock_data.append(stock_datum)
                stock_set.append(stock_datum)
                rest -= assigned
        if build_venue: 
            retval.venue = one_to_many(
                [self.build_venue_datum(organization, site, stock_sets)],
                'performance_id'
                )
        retval.stocks = one_to_many(
            stock_data,
            'performance_id'
            )
        retval.product_items = one_to_many(
            list(chain(*(
                self.build_product_item_data(organization, retval, product, stock_data) \
                for product in event.products
                ))),
            'performance_id'
            )
        order_data = []
        for _ in range(0, 10):
            try:
                order_data.append(
                    self.build_order_datum(
                        organization,
                        choice(self.user_data),
                        choice(event.sales_segments),
                        retval,
                        [
                            (product, randint(1, 3))
                            for product in sample(event.products, randint(1, 3))
                            ]
                        )
                    )
            except NotEnoughStockError, e:
                logger.info(e)

        retval.orders = one_to_many(
            order_data,
            'performance_id'
            )

        return retval

    def build_stock_type_datum(self, name, type, quantity_only):
        return self.Datum(
            'StockType',
            name=name,
            type=type,
            quantity_only=quantity_only,
            style=json.dumps(dict(fill=dict(color=random_color())), ensure_ascii=False)
            )

    def build_product_item(self, performance, product, stock, price, quantity):
        return self.Datum(
            'ProductItem',
            price=price,
            stock=many_to_one(stock, 'stock_id'),
            product=many_to_one(product, 'product_id'),
            performance=many_to_one(performance, 'performance_id'),
            quantity=quantity
            )

    def build_product_item_data(self, organization, performance, product, stocks):
        def find_stock(stock_type_name):
            for stock in stocks:
                if stock.stock_type.name == stock_type_name and \
                   stock.stock_holder is not None and \
                   stock.stock_holder.account.user == organization.user:
                    return stock
            raise Exception("No such stock that corresponds to %s" % stock_type_name)

        product_item_seeds = self.stock_type_combinations[product.name]
        return [
            self.build_product_item(
                performance, product,
                find_stock(stock_type_name), price, 1)
                for stock_type_name, price in product_item_seeds
            ]

    def build_product_data(self, sales_segment):
        return [
            self.Datum(
                'Product',
                name=name,
                price=sum(price for stock_type_name, price in product_item_seeds),
                sales_segment=many_to_one(sales_segment, 'sales_segment_id')
                ) \
            for name, product_item_seeds in self.stock_type_combinations.iteritems()
            ]

    def pick_stocks(self, performance, product_item):
        if product_item.stock.stock_type.type == STOCK_TYPE_TYPE_SEAT:
            venue = performance.venue[0]
            seats = sample([seat for seat in venue.seats if seat.status_[0].status == 1], product_item.quantity)
        else:
            seats = []
        return seats

    def build_ordered_product_datum(self, performance, product, quantity):
        product_items = [
            product_item
            for product_item in performance.product_items
            if product_item.product == product
            ]
        return self.Datum(
            'OrderedProduct',
            product=many_to_one(product, 'product_id'),
            price=product.price,
            quantity=quantity,
            ordered_product_items=one_to_many(
                [
                    self.Datum(
                        'OrderedProductItem',
                        product_item=many_to_one(product_item, 'product_item_id'),
                        seats=many_to_many(
                            self.pick_stocks(performance, product_item),
                            'OrderedProductItem_id',
                            'seat_id',
                            'orders_seat'
                            ),
                        price=product_item.price
                        )
                    for product_item in product_items
                    ],
                'ordered_product_id'
                )
            )

    def build_order_datum(self, organization, user, sales_segment, performance, product_quantity_pairs):
        ordered_products = [
            self.build_ordered_product_datum(performance, product, quantity)
            for product, quantity in product_quantity_pairs
            ]

        # check availability
        summaries = {}
        for ordered_product in ordered_products:
            for ordered_product_item in ordered_product.ordered_product_items:
                product_item = ordered_product_item.product_item
                stock = product_item.stock
                if stock not in summaries:
                    summaries[stock] = [stock.stock_status[0].quantity, 0]
                summaries[stock][1] += product_item.quantity * ordered_product.quantity

        for stock, (available, needed) in summaries.items():
            if available < needed:
                raise NotEnoughStockError("OutOfStock (%s < %d; total=%d)" % (available, needed, stock.quantity))

        # decrement availability
        for ordered_product in ordered_products:
            for ordered_product_item in ordered_product.ordered_product_items:
                product_item = ordered_product_item.product_item
                product_item.stock.stock_status[0].quantity -= product_item.quantity * ordered_product.quantity
                assert product_item.stock.stock_status[0].quantity >= 0
                for seat in ordered_product_item.seats:
                    seat.status_[0].status = SeatStatusEnum.Shipped.v # Shipped

        payment_delivery_method_pair = choice(sales_segment.payment_delivery_method_pairs)
        total_amount = sum(
            ordered_product.price * ordered_product.quantity
            for ordered_product in ordered_products
            ) \
            + payment_delivery_method_pair.system_fee \
            + payment_delivery_method_pair.transaction_fee \
            + payment_delivery_method_pair.delivery_fee

        paid_at = some_day_between(sales_segment.start_at, sales_segment.end_at)

        return self.Datum(
            'Order',
            user=many_to_one(user, 'user_id'),
            shipping_address=many_to_one(self.build_shipping_address_datum(user), 'shipping_address_id'),
            organization=many_to_one(organization, 'organization_id'),
            performance=many_to_one(performance, 'performance_id'),
            order_no=random_order_number(organization),
            items=one_to_many(ordered_products, 'order_id'),
            total_amount=total_amount,
            system_fee=payment_delivery_method_pair.system_fee,
            transaction_fee=payment_delivery_method_pair.transaction_fee,
            delivery_fee=payment_delivery_method_pair.delivery_fee,
            payment_delivery_method_pair=many_to_one(payment_delivery_method_pair, 'payment_delivery_method_pair_id'),
            paid_at=paid_at,
            delivered_at=paid_at + relativedelta(days=randint(0, 3))
            )

    def build_event_datum(self, organization, title):
        logger.info(u"Building Event %s" % title)
        event_date = random_date()
        stock_type_data = [
            self.build_stock_type_datum(_name, type, quantity_only)
            for _name, type, quantity_only in self.stock_type_triplets
            ]
        sales_segment_data = [
            self.build_sales_segment_datum(
                organization,
                u'先行',
                datetime.combine(event_date, time(10, 0)) + relativedelta(months=-3),
                datetime.combine(event_date, time(0, 0)) + relativedelta(months=-2, seconds=-1)
                ),
            self.build_sales_segment_datum(
                organization,
                u'一般',
                datetime.combine(event_date, time(10, 0)) + relativedelta(months=-2),
                datetime.combine(event_date, time(0, 0)) + relativedelta(seconds=-1)
                )
            ]
        stock_holder_data = [
            self.Datum(
                'StockHolder',
                name=account.name,
                account=many_to_one(account, 'account_id'),
                style=json.dumps(dict(text=account.name[0]), ensure_ascii=False)
                ) \
            for account in organization.accounts
            ]
        product_data = list(chain(*(
            self.build_product_data(sales_segment_datum) \
            for sales_segment_datum in sales_segment_data
            )))

        retval = self.Datum(
            'Event',
            title=title,
            organization=many_to_one(organization, 'organization_id'),
            stock_types=one_to_many(
                stock_type_data,
                'event_id'
                ),
            account=many_to_one(choice(organization.accounts), 'account_id'),
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
                    event_date + relativedelta(days=i)) \
                for i, name in enumerate(self.performance_names)
                ],
            'event_id'
            )
        return retval

    def build_shipping_address_datum(self, user):
        return self.Datum(
            'ShippingAddress',
            user=many_to_one(user, 'user_id'),
            email=lambda self: "dev+test%03d@ticketstar.jp" % self._id[0],
            first_name=lambda self: u"太郎%d" % self._id[0],
            last_name=u"楽天",
            first_name_kana=u"タロウ",
            last_name_kana=u"ラクテン",
            zip="251-0036",
            prefecture=u"東京都",
            city=u"品川区",
            address_1=u"東五反田5-21-15'",
            address_2=u"メタリオンOSビル",
            tel_1=u"03-9999-9999",
            tel_2=u"090-0000-0000",
            fax=u"03-9876-5432"
            )

