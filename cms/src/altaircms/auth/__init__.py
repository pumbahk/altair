from .interfaces import ILogoutAction

def includeme(config):
    """
    requirement in settings:
    
    altaircms.logout.external.url
    altaircms.logout.action
    """
    settings = config.registry.settings
    url = settings.get("altaircms.logout.external.url")
    logout_action_class = config.maybe_dotted(settings.get("altaircms.logout.action"))
    config.registry.registerUtility(logout_action_class(url), ILogoutAction)

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('oauth_entry', '/oauth')
    config.add_route('oauth_callback', '/oauth_callback')

    config.add_route('operator_list', '/operator/')
    config.add_route('operator', '/operator/{id}')

    config.add_route('role_list', '/role/')
    config.add_route('role', '/role/{id}')

    config.add_route('role_permission', '/role/{role_id}/permission/{id}')

    config.scan()
