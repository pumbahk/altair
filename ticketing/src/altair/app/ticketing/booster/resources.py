import logging
from pyramid.decorator import reify
import sqlalchemy as sa
from webob.multidict import MultiDict

from altair.app.ticketing.cart.resources import EventOrientedTicketingCartResource
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Product
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.users.models import User, UserCredential, Membership
from altair.app.ticketing.sej.models import SejOrder
from altair.app.ticketing.core.api import get_organization
from altair.app.ticketing.sej import api as sej_api
from .api import store_user_profile
from .api import remove_user_profile
from .api import load_user_profile

from .api import get_booster_settings
from altair.app.ticketing.cart.helpers import products_filter_by_salessegment
logger = logging.getLogger(__name__)

class BoosterCartResource(EventOrientedTicketingCartResource):
    @reify
    def membership_name(self):
        return get_booster_settings(self.request).membership_name

    def _populate_params(self):
        self._event_id = get_booster_settings(self.request).event_id
        self._sales_segment_id = None

    def product_form(self, params):
        raise Exception

    def product_form_from_user_profile(self, user_profile):
        params = MultiDict()
        if user_profile is not None:
            def _(items, prefix):
                for k, v in items:
                    if isinstance(v, dict):
                        _(v.items(), k + u'-')
                    else:
                        if v is not None:
                            params[prefix + k] = v
            _(user_profile.items(), u'')
        return self.product_form(params)

    @reify
    def products_dict(self):
        return {str(p.id): p for p in  self.product_query}

    def store_user_profile(self, data):
        return store_user_profile(self.request, data)

    def load_user_profile(self):
        return load_user_profile(self.request)

    def remove_user_profile(self):
        return remove_user_profile(self.request)

    @reify 
    def product_query(self):
        query = Product.query
        query = query.filter(Product.sales_segment_id == self.sales_segment.id, Product.public != False)
        salessegment = self.get_sales_segment()
        return products_filter_by_salessegment(query, salessegment).order_by(Product.display_order)

    @reify
    def sales_segment(self):
        return self.available_sales_segments[0]

    def get_order(self):
        organization = get_organization(self.request)
        order_no = self.request.params.get('order_no')
        order = Order.filter_by(
            organization_id=organization.id,
            order_no=order_no
        ).first()
        logger.debug("organization_id=%s, order_no=%s, order=%s" % (organization.id, order_no, order))
        sej_order = None
        if order:
            payment_method_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin.id
            if payment_method_plugin_id == 1:
                pass
            elif payment_method_plugin_id == 3:
                sej_order = sej_api.get_sej_order(order_no)

        return order, sej_order

