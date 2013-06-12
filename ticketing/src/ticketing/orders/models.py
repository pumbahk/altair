import sqlalchemy as sa
from sqlalchemy.sql import and_
from pyramid.threadlocal import get_current_request
import sqlalchemy.orm as orm

from ticketing.core.models import (
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
)
from ticketing.users.models import (
    User,
    UserProfile,
    Membership,
    MemberGroup,
    UserCredential,
)
from ticketing.models import (
    Base,
    DBSession,
)


order_summary = sa.select([
    Order.id,
    Order.organization_id,
    Order.order_no,
    Order.created_at,
    Order.paid_at,
    Order.delivered_at,
    Order.canceled_at,
    Order.refund_id,
    Order.refunded_at,
    Order.transaction_fee,
    Order.delivery_fee,
    Order.system_fee,
    Order.total_amount,
    Order.note,
    Order.card_brand,
    Order.card_ahead_com_code,
    Order.card_ahead_com_name,
    UserProfile.last_name.label('user_profile_last_name'),
    UserProfile.first_name.label('user_profile_first_name'),
    UserProfile.last_name_kana.label('user_profile_last_name_kana'),
    UserProfile.first_name_kana.label('user_profile_first_name_kana'),
    UserProfile.nick_name.label('user_profile_nick_name'),
    UserProfile.sex.label('user_profile_sex'),
    Membership.name.label('membership_name'),
    MemberGroup.name.label('membergroup_name'),
    UserCredential.auth_identifier,
    ShippingAddress.last_name,
    ShippingAddress.first_name,
    ShippingAddress.last_name_kana,
    ShippingAddress.first_name_kana,
    ShippingAddress.zip,
    ShippingAddress.country,
    ShippingAddress.prefecture,
    ShippingAddress.city,
    ShippingAddress.address_1,
    ShippingAddress.address_2,
    ShippingAddress.fax,
    ShippingAddress.email_1,
    ShippingAddress.email_2,
    PaymentMethod.name.label('payment_method_name'),
    DeliveryMethod.name.label('delivery_method_name'),
    #Event.id.label("event_id"),
    #Event.title,
    #Performance.id.label('performance_id'),
    #Performance.name.label('performance_name'),
    #Performance.code,
    #Performance.start_on,
    Order.performance_id,
    #Venue.name.label('venue_name'),
], from_obj=[Order.__table__.join(
    ShippingAddress.__table__,
    Order.shipping_address_id==ShippingAddress.id
    #).join(
    #Performance.__table__,
    #Order.performance_id==Performance.id
).join(
    PaymentDeliveryMethodPair.__table__,
    Order.payment_delivery_method_pair_id==PaymentDeliveryMethodPair.id,
).join(
    PaymentMethod.__table__,
    PaymentDeliveryMethodPair.payment_method_id==PaymentMethod.id,
).join(
    DeliveryMethod.__table__,
    PaymentDeliveryMethodPair.delivery_method_id==DeliveryMethod.id,
    #).join(
    #Event.__table__,
    #Performance.event_id==Event.id,
    #).join(
    #Venue.__table__,
    #Venue.performance_id==Performance.id,
).outerjoin(
    User.__table__,
    Order.user_id==User.id,
).outerjoin(
    UserProfile.__table__,
    User.id==UserProfile.user_id,
).outerjoin(
    UserCredential.__table__,
    User.id==UserCredential.user_id,
).outerjoin(
    Membership.__table__,
    UserCredential.membership_id==Membership.id,
).outerjoin(
    MemberGroup.__table__,
    MemberGroup.membership_id==Membership.id,
)]).alias()

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
    def __init__(self, id, start_on, event, venue):
        self.id = id
        self.start_on = start_on
        self.event = event
        self.venue = venue

class SummarizedShippingAddress(object):
    def __init__(self, last_name, first_name, last_name_kana, first_name_kana, zip, country, prefecture, city, address_1, address_2, fax, email_1, email_2):
        self.last_name = last_name
        self.first_name = first_name
        self.last_name_kana = last_name_kana
        self.first_name_kana = first_name_kana
        self.zip = zip
        self.country = country
        self.prefecture = prefecture
        self.city = city
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
            performances[row.performance_id] = SummarizedPerformance(row.performance_id,
                                                                     row.start_on,
                                                                     SummarizedEvent(row.event_id,
                                                                                     row.title),
                                                                     SummarizedVenue(row.venue_name))
        request._performances = performances
    return request._performances

def _get_performance(request, performance_id, organization_id):
    performances = _get_performances(request, organization_id)
    return performances[performance_id]

class OrderSummary(Base):
    __table__ = order_summary
    query = DBSession.query_property()

    ordered_products = orm.relationship('OrderedProduct')
    refund = orm.relationship('Refund')

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
        return None

    @property
    def shipping_address(self):
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
            self.fax,
            self.email_1,
            self.email_2,
        )

    @property
    def payment_delivery_pair(self):
        return SummarizedPaymentDeliveryMethodPair(None, None)

    @property
    def performance(self):
        # return SummarizedPerformance(self.performance_id,
        #                              self.start_on,
        #                              SummarizedEvent(self.event_id, self.title),
        #                              SummarizedVenue(self.venue_name))
        request = get_current_request()
        return _get_performance(request, self.performance_id, self.organization_id)

    @property
    def cancel_reason(self):
        return self.refund.cancel_reason if self.refund else None
