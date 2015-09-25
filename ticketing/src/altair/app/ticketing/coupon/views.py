from altair.now import get_now, is_now_set
from pyramid.httpexceptions import HTTPNotFound
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart.rendering import selectable_renderer


class CouponView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(
        route_name='coupon',
        renderer=selectable_renderer("coupon.html"))
    def show(self):

        reserved_number = self.context.get_reserved_number(self.request.matchdict.get('reserved_number', None))
        if reserved_number is None:
            raise HTTPNotFound()

        order = self.context.get_order(reserved_number.order_no)
        if order is None:
            raise HTTPNotFound()

        return dict(
            reserved_number=reserved_number,
            order=order
            )

    @lbr_view_config(
        route_name='coupon_admission',
        request_method='POST',
        renderer=selectable_renderer("admission.html"))
    def admission(self):
        order = self.context.get_order(self.request.matchdict['order_no'])
        if order is None:
            raise HTTPNotFound

        now = get_now(self.request)
        order.printed_at = now

        for attr in order.items:
            for element in attr.elements:
                element.printed_at = now
                for token in element.tokens:
                    token.printed_at = now

        return dict(
            order=order
            )

