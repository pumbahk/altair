from pyramid.tweens import MAIN

# List of route names possible to be requested from R-Live App
# Route names need to contain performance_id or lot_id
R_LIVE_REQUEST_ROUTES = (
    'cart.index2',
    'cart.agreement2',
    'cart.spa.agreement',
    'cart.agreement2.compat',
    'cart.switchpc.perf',
    'cart.switchsp.perf',
    'cart.spa.index',
    'lots.entry.agreement',
    'lots.entry.agreement.compat',
    'lots.entry.index',
)


def includeme(config):
    config.add_tween('.tweens.r_live_request_tween_factory', over=MAIN)
    config.include('.communicator')
