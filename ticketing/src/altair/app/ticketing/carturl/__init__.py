class BUILDERS:
    cart = "cart"
    cart_now = "cart.now"
    lots_cart = "cart.lots"
    agreement_cart = "cart.agreement"
    agreement_lots_cart = "cart.agreement_lots"

def includeme(config):
    from .interfaces import IURLBuilder
    from .carturl import CartURLBuilder
    config.registry.registerUtility(CartURLBuilder(path_prefix="/cart/events"), IURLBuilder, name=BUILDERS.cart)

    from .carturl import CartNowURLBuilder
    config.registry.registerUtility(CartNowURLBuilder(path_prefix="/whattime/login"), IURLBuilder, name=BUILDERS.cart_now)

    from .carturl import LotsCartURLBuilder
    config.registry.registerUtility(LotsCartURLBuilder(path_prefix="/lots/events"), IURLBuilder, name=BUILDERS.lots_cart)

    from .carturl import AgreementCartURLBuilder
    config.registry.registerUtility(AgreementCartURLBuilder(path_prefix="/cart/events"), IURLBuilder, name=BUILDERS.agreement_cart)

    from .carturl import AgreementLotsCartURLBuilder
    config.registry.registerUtility(AgreementLotsCartURLBuilder(path_prefix="/lots/events"), IURLBuilder, name=BUILDERS.agreement_lots_cart)
