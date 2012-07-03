def includeme(config):
    """
    requirement in settings:
    
    altaircms.logout.external.url
    altaircms.logout.action

    for oauth login:
    altair.oauth.client_id
    altair.oauth.secret_key
    altair.oauth.authorize_url
    altair.oauth.access_token_url
    """
    settings = config.registry.settings
    url = settings.get("altaircms.logout.external.url")
    logout_action_class = config.maybe_dotted(settings.get("altaircms.logout.action"))
    config.registry.registerUtility(logout_action_class(url), 
                                    config.maybe_dotted(".interfaces.ILogoutAction"))

    oauth_component_class = config.maybe_dotted(".api.OAuthComponent")
    oauth_component = oauth_component_class(
        settings["altair.oauth.client_id"], 
        settings["altair.oauth.secret_key"], 
        settings["altair.oauth.authorize_url"], 
        settings["altair.oauth.access_token_url"], 
        )
    config.registry.registerUtility(oauth_component, 
                                    config.maybe_dotted(".interfaces.IOAuthComponent"))
    ## bind event
    config.add_subscriber(".subscribers.touch_operator_after_login", ".subscribers.AfterLogin")


    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('oauth_entry', '/oauth')
    config.add_route('oauth_callback', '/oauth_callback')

    config.add_route('operator_list', '/operator/')
    config.add_route('operator_info', '/operator/info')
    config.add_route('operator', '/operator/{id}')

    config.add_route('role_list', '/role/')
    config.add_route('role', '/role/{id}')

    config.add_route('role_permission', '/role/{role_id}/permission/{id}')

    config.scan()
