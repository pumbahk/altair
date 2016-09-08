class BUILDERS:
    cart_events = "cart.events"
    cart_performances = "cart.performances"
    cart_now = "cart.now"
    lots_cart = "cart.lots"
    agreement_cart = "cart.agreement"
    agreement_lots_cart = "cart.agreement_lots"
    orderreview_qr = "orderreview.qr"

def includeme(config):
    from .interfaces import IURLBuilder
    from .carturl import CartURLEventsBuilder
    config.registry.registerUtility(CartURLEventsBuilder(path_prefix="/cart/events"), IURLBuilder, name=BUILDERS.cart_events)

    from .carturl import CartURLPerformanceBuilder
    config.registry.registerUtility(CartURLPerformanceBuilder(path_prefix="/cart/performances"), IURLBuilder, name=BUILDERS.cart_performances)

    from .carturl import CartNowURLBuilder
    config.registry.registerUtility(CartNowURLBuilder(path_prefix="/whattime/login"), IURLBuilder, name=BUILDERS.cart_now)

    from .carturl import LotsCartURLBuilder
    config.registry.registerUtility(LotsCartURLBuilder(path_prefix="/lots/events"), IURLBuilder, name=BUILDERS.lots_cart)

    from .carturl import AgreementCartURLBuilder
    config.registry.registerUtility(AgreementCartURLBuilder(path_prefix="/cart/events"), IURLBuilder, name=BUILDERS.agreement_cart)

    from .carturl import AgreementLotsCartURLBuilder
    config.registry.registerUtility(AgreementLotsCartURLBuilder(path_prefix="/lots/events"), IURLBuilder, name=BUILDERS.agreement_lots_cart)

    from .carturl import OrderReviewQRURLBuilder
    config.registry.registerUtility(OrderReviewQRURLBuilder(path_prefix="/orderreview"), IURLBuilder, name=BUILDERS.orderreview_qr)

