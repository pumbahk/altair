from pyramid.decorator import reify

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Organization, Event
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.cart.models import CartSetting

class CartSettingListResource(TicketingAdminResource):
    @property
    def cart_settings(self):
        return DBSession.query(CartSetting) \
            .filter(CartSetting.organization_id == self.organization.id ) \
            .order_by(CartSetting.display_order, CartSetting.id)

class CartSettingResource(TicketingAdminResource):
    def __init__(self, request):
        super(CartSettingResource, self).__init__(request)
        try:
            cart_setting_id = long(request.matchdict['cart_setting_id'])
        except (TypeError, ValueError):
            cart_setting_id = None
        self._cart_setting_id = cart_setting_id

    @reify
    def cart_setting(self):
        return DBSession.query(CartSetting) \
            .filter(CartSetting.organization_id == self.organization.id) \
            .filter(CartSetting.id == self._cart_setting_id) \
            .one()
