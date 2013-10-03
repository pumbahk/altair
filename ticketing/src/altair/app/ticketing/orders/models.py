import sqlalchemy as sa
from sqlalchemy.sql import and_
from pyramid.threadlocal import get_current_request
import sqlalchemy.orm as orm
from sqlalchemy.sql.expression import desc
from altair.sqla import session_partaken_by

from altair.app.ticketing.core.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    ShippingAddress,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    Event,
    Performance,
    Venue,
    Seat,
    Refund,
    ShippingAddressMixin,
)
from altair.app.ticketing.users.models import (
    User,
    UserProfile,
    Member,
    Membership,
    UserCredential,
)
from altair.app.ticketing.sej.models import (
    SejOrder,
)
from altair.app.ticketing.models import (
    Base,
)


class SummarizedUser(object):
    def __init__(self, session, id, user_profile, user_credential):
        self.session = session
        self.id = id
        self.user_profile = user_profile
        self.user_credential = [user_credential]
        self.first_user_credential = user_credential

    @property
    def member(self):
        return self.session.query(Member).filter_by(user_id=self.id).first()

class SummarizedUserCredential(object):
    def __init__(self, auth_identifier, membership):
        self.auth_identifier = auth_identifier
        self.membership = membership

class SummarizedMembership(object):
    def __init__(self, name):
        self.name = name

class SummarizedUserProfile(object):
    def __init__(self,
                 last_name,
                 first_name,
                 last_name_kana,
                 first_name_kana,
                 nick_name,
                 sex,):
        self.last_name = last_name
        self.first_name = first_name
        self.last_name_kana = last_name_kana
        self.first_name_kana = first_name_kana
        self.nick_name = nick_name
        self.sex = sex

class SummarizedPaymentMethod(object):
    def __init__(self, name):
        self.name = name

class SummarizedDeliveryMethod(object):
    def __init__(self, name):
        self.name = name

class SummarizedPaymentDeliveryMethodPair(object):
    def __init__(self, payment_method, delivery_method):
        self.payment_method = payment_method
        self.delivery_method = delivery_method

class SummarizedEvent(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title

class SummarizedVenue(object):
    def __init__(self, name):
        self.name = name

class SummarizedPerformance(object):
    def __init__(self, id, name, code, start_on, event, venue):
        self.id = id
        self.name = name
        self.code = code
        self.start_on = start_on
        self.event = event
        self.venue = venue

class SummarizedShippingAddress(ShippingAddressMixin):
    def __init__(self, last_name, first_name, last_name_kana, first_name_kana, zip, country, prefecture, city, address_1, address_2, tel_1, tel_2, fax, email_1, email_2):
        self.last_name = last_name
        self.first_name = first_name
        self.last_name_kana = last_name_kana
        self.first_name_kana = first_name_kana
        self.zip = zip
        self.country = country
        self.prefecture = prefecture
        self.city = city
        self.tel_1 = tel_1
        self.tel_2 = tel_2
        self.address_1 = address_1
        self.address_2 = address_2
        self.fax = fax
        self.email_1 = email_1
        self.email_2 = email_2

def _get_performances(request, organization_id):
    if not hasattr(request, "_performances"):
        results = sa.select(
            [
                Event.id.label("event_id"),
                Event.title,
                Performance.id.label('performance_id'),
                Performance.name.label('performance_name'),
                Performance.code,
                Performance.start_on,
                Venue.name.label('venue_name'),
            ],
            Event.organization_id==organization_id,
            from_obj=[
                Performance.__table__.join(
                    Event.__table__,
                ).join(
                    Venue.__table__,
                )]).execute()

        performances = {}
        for row in results:
            performances[row.performance_id] = SummarizedPerformance(
                row.performance_id,
                row.performance_name,
                row.code,
                row.start_on,
                SummarizedEvent(
                    row.event_id,
                    row.title
                    ),
                SummarizedVenue(row.venue_name)
                )
        request._performances = performances
    return request._performances

def _get_performance(request, performance_id, organization_id):
    performances = _get_performances(request, organization_id)
    return performances[performance_id]


class HybridRelation(object):
    def __init__(self, instance_property, relationship):
        self.instance_property = instance_property
        self.relationship = relationship

    def __get__(self, obj, type=None):
        if obj:
            return self.instance_property(obj)
        else:
            return self.relationship


class OrderSummary(Base):
    __mapper_args__ = dict(
        include_properties=[
            Order.__table__.c.id,
            Order.__table__.c.organization_id,
            Performance.__table__.c.event_id,
            Performance.__table__.c.start_on,
            Performance.__table__.c.end_on,
            Order.__table__.c.performance_id,
            Order.__table__.c.order_no,
            Order.__table__.c.created_at,
            Order.__table__.c.paid_at,
            Order.__table__.c.delivered_at,
            Order.__table__.c.canceled_at,
            Order.__table__.c.refund_id,
            Order.__table__.c.refunded_at,
            Order.__table__.c.transaction_fee,
            Order.__table__.c.delivery_fee,
            Order.__table__.c.system_fee,
            Order.__table__.c.total_amount,
            Order.__table__.c.note,
            Order.__table__.c.card_brand,
            Order.__table__.c.card_ahead_com_code,
            Order.__table__.c.card_ahead_com_name,
            Order.__table__.c.payment_delivery_method_pair_id,
            Order.__table__.c.shipping_address_id,
            Order.__table__.c.issued,
            Order.__table__.c.user_id,
            Order.__table__.c.created_at,
            Order.__table__.c.deleted_at,
            UserProfile.__table__.c.last_name.label('user_profile_last_name'),
            UserProfile.__table__.c.first_name.label('user_profile_first_name'),
            UserProfile.__table__.c.last_name_kana.label('user_profile_last_name_kana'),
            UserProfile.__table__.c.first_name_kana.label('user_profile_first_name_kana'),
            UserProfile.__table__.c.nick_name.label('user_profile_nick_name'),
            UserProfile.__table__.c.sex.label('user_profile_sex'),
            UserCredential.__table__.c.auth_identifier,
            ShippingAddress.__table__.c.last_name,
            ShippingAddress.__table__.c.first_name,
            ShippingAddress.__table__.c.last_name_kana,
            ShippingAddress.__table__.c.first_name_kana,
            ShippingAddress.__table__.c.zip,
            ShippingAddress.__table__.c.country,
            ShippingAddress.__table__.c.prefecture,
            ShippingAddress.__table__.c.city,
            ShippingAddress.__table__.c.tel_1,
            ShippingAddress.__table__.c.tel_2,
            ShippingAddress.__table__.c.address_1,
            ShippingAddress.__table__.c.address_2,
            ShippingAddress.__table__.c.fax,
            ShippingAddress.__table__.c.email_1,
            ShippingAddress.__table__.c.email_2,
            PaymentMethod.__table__.c.name.label('payment_method_name'),
            DeliveryMethod.__table__.c.name.label('delivery_method_name'),
            Membership.__table__.c.name.label('membership_name')
            ],
        primary_key=[
            Order.__table__.c.id
            ],
        )

    id = Order.id
    organization_id = Order.organization_id
    event_id = Performance.event_id
    performance_start_on = Performance.start_on
    performance_end_on = Performance.end_on
    performance_id = Order.performance_id
    order_no = Order.order_no
    created_at = Order.created_at
    paid_at = Order.paid_at
    delivered_at = Order.delivered_at
    canceled_at = Order.canceled_at
    refund_id = Order.refund_id
    refunded_at = Order.refunded_at
    transaction_fee = Order.transaction_fee
    delivery_fee = Order.delivery_fee
    system_fee = Order.system_fee
    total_amount = Order.total_amount
    note = Order.note
    card_brand = Order.card_brand
    card_ahead_com_code = Order.card_ahead_com_code
    card_ahead_com_name = Order.card_ahead_com_name
    payment_delivery_method_pair_id = Order.payment_delivery_method_pair_id
    shipping_address_id = Order.shipping_address_id
    issued = Order.issued
    user_id = Order.user_id
    created_at = Order.created_at
    deleted_at = Order.deleted_at
    user_profile_last_name = UserProfile.__table__.c.last_name
    user_profile_first_name = UserProfile.__table__.c.first_name
    user_profile_last_name_kana = UserProfile.__table__.c.last_name_kana
    user_profile_first_name_kana = UserProfile.__table__.c.first_name_kana
    user_profile_nick_name = UserProfile.__table__.c.nick_name
    user_profile_sex = UserProfile.__table__.c.sex
    auth_identifier = UserCredential.auth_identifier
    last_name = ShippingAddress.last_name
    first_name = ShippingAddress.first_name
    last_name_kana = ShippingAddress.last_name_kana
    first_name_kana = ShippingAddress.first_name_kana
    zip = ShippingAddress.zip
    country = ShippingAddress.country
    prefecture = ShippingAddress.prefecture
    city = ShippingAddress.city
    tel_1 = ShippingAddress.tel_1
    tel_2 = ShippingAddress.tel_2
    address_1 = ShippingAddress.address_1
    address_2 = ShippingAddress.address_2
    fax = ShippingAddress.fax
    email_1 = ShippingAddress.email_1
    email_2 = ShippingAddress.email_2
    payment_method_id = PaymentMethod.id
    payment_method_name = PaymentMethod.__table__.c.name
    delivery_method_id = DeliveryMethod.id
    delivery_method_name = DeliveryMethod.__table__.c.name
    membership_name = Membership.__table__.c.name

    __table__ = Order.__table__ \
        .join(
            PaymentDeliveryMethodPair.__table__,
            and_(Order.payment_delivery_method_pair_id==PaymentDeliveryMethodPair.id,
                 PaymentDeliveryMethodPair.deleted_at==None)
            ) \
        .join(
            PaymentMethod.__table__,
            and_(PaymentDeliveryMethodPair.payment_method_id==PaymentMethod.id,
                 PaymentMethod.deleted_at==None)
            ) \
        .join(
            DeliveryMethod.__table__,
            and_(PaymentDeliveryMethodPair.delivery_method_id==DeliveryMethod.id,
                 DeliveryMethod.deleted_at==None)
            ) \
        .join(
            Performance.__table__,
            and_(Performance.id==Order.performance_id,
                 Performance.deleted_at==None)
            ) \
        .outerjoin(
            ShippingAddress.__table__,
            and_(Order.shipping_address_id==ShippingAddress.id,
                 ShippingAddress.deleted_at==None)
            ) \
        .outerjoin(
            User.__table__,
            and_(Order.user_id==User.id,
                 User.deleted_at==None)
            ) \
        .outerjoin(
            UserProfile.__table__,
            and_(User.id==UserProfile.user_id,
                 UserProfile.deleted_at==None)
            ) \
        .outerjoin(
            UserCredential.__table__,
            and_(User.id==UserCredential.user_id,
                 UserCredential.deleted_at==None)
            ) \
        .outerjoin(
            Membership.__table__,
            and_(UserCredential.membership_id==Membership.id,
                 Membership.deleted_at==None)
        )

    ordered_products = orm.relationship('OrderedProduct', primaryjoin=Order.id==OrderedProduct.order_id)
    refund = orm.relationship('Refund', primaryjoin=Order.refund_id==Refund.id)

    @property
    def status(self):
        if self.canceled_at:
            return 'canceled'
        elif self.delivered_at:
            return 'delivered'
        else:
            return 'ordered'

    @property
    def payment_status(self):
        if self.refund_id and not self.refunded_at:
            return 'refunding'
        elif self.refunded_at:
            return 'refunded'
        elif self.paid_at:
            return 'paid'
        else:
            return 'unpaid'

    @property
    def user(self):
        return SummarizedUser(
            session_partaken_by(self),
            self.user_id,
            SummarizedUserProfile(
                self.user_profile_last_name,
                self.user_profile_first_name,
                self.user_profile_last_name_kana,
                self.user_profile_first_name_kana,
                self.user_profile_nick_name,
                self.user_profile_sex
                ),
            SummarizedUserCredential(
                self.auth_identifier,
                SummarizedMembership(
                    self.membership_name
                    )
                )
            )

    @property
    def sej_order(self):
        return SejOrder.query.filter_by(order_no=self.order_no).order_by(desc(SejOrder.branch_no)).first()

    def _shipping_address(self):
        if self.shipping_address_id is None:
            return None

        return SummarizedShippingAddress(
            self.last_name,
            self.first_name,
            self.last_name_kana,
            self.first_name_kana,
            self.zip,
            self.country,
            self.prefecture,
            self.city,
            self.address_1,
            self.address_2,
            self.tel_1,
            self.tel_2,
            self.fax,
            self.email_1,
            self.email_2,
        )
    rel_shipping_address = orm.relationship("ShippingAddress", primaryjoin=Order.shipping_address_id==ShippingAddress.id)
    shipping_address = HybridRelation(_shipping_address, rel_shipping_address)

    def _payment_delivery_pair(self):
        return SummarizedPaymentDeliveryMethodPair(
            SummarizedPaymentMethod(self.payment_method_name),
            SummarizedDeliveryMethod(self.delivery_method_name))

    rel_payment_delivery_pair = orm.relationship("PaymentDeliveryMethodPair", primaryjoin=Order.payment_delivery_method_pair_id==PaymentDeliveryMethodPair.id)
    payment_delivery_pair = HybridRelation(_payment_delivery_pair, rel_payment_delivery_pair)

    def _performance(self):
        request = get_current_request()
        return _get_performance(request, self.performance_id, self.organization_id)

    rel_performance = orm.relationship("Performance")
    performance = HybridRelation(_performance, rel_performance)

    @property
    def cancel_reason(self):
        return self.refund.cancel_reason if self.refund else None
