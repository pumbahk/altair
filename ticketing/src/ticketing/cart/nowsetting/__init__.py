def find_group(user_id, request):
    return ["group:cart_admin"]

def includeme(config):
    config.add_route("cart.nowsetting.form", "/form", factory=".resources.CartAdminResource")
    config.add_route("cart.nowsetting.set", "/set", factory=".resources.CartAdminResource")

    settings = config.registry.settings
    config.include("ticketing.login.internal")
    config.use_internal_login(secret=settings['authtkt.secret'], cookie_name='printqr.auth_tkt', auth_callback=find_group)
    config.setup_internal_login_views(factory=".resources.CartAdminResource", login_html="ticketing.cart:templates/__default__/pc/nowsetting/login.html")

    config.scan(".views")
