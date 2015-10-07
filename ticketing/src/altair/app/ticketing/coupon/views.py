from pyramid.view import view_defaults
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart.rendering import selectable_renderer
from pyramid.httpexceptions import HTTPFound


class CouponErrorView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='coupon.notfound', renderer=selectable_renderer("notfound.html"))
    def notfound(self):
        return dict()


@view_defaults(renderer=selectable_renderer("coupon.html"))
class CouponView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='coupon')
    def show(self):

        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('coupon.notfound'))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order
            )

    @lbr_view_config(
        route_name='coupon.admission', request_method='POST')
    def admission(self):
        order = self.context.order
        if order is None:
            return HTTPFound(location=self.request.route_path('coupon.notfound'))

        self.context.use_coupon()

        return dict(
            reserved_number=self.context.reserved_number,
            order=order
            )
