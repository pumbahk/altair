from pyramid_layout.panel import panel_config
from altair.app.ticketing.cart.rendering import selectable_renderer

@panel_config('order_detail.standard', renderer=selectable_renderer('order_review/_order_detail_standard.html'))
def order_detail_standard(context, request, order):
    return { 'order': order }

@panel_config('order_detail.booster.89ers', renderer=selectable_renderer('order_review/_order_detail_booster.html'))
@panel_config('order_detail.booster.bambitious', renderer=selectable_renderer('order_review/_order_detail_booster.html'))
@panel_config('order_detail.booster.bigbulls', renderer=selectable_renderer('order_review/_order_detail_booster.html'))
def order_detail_booster(context, request, order):
    return { 'order': order }

@panel_config('order_detail.fc', renderer=selectable_renderer('order_review/_order_detail_fc.html'))
def order_detail_fc(context, request, order):
    return { 'order': order }
