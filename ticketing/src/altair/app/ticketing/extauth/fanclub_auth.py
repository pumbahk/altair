# encoding: UTF-8


def get_fanclub_auth_setting(request, k):
    settings = request.organization.settings
    if settings is not None:
        fanclub_auth_settings = settings.get(u'rakuten_auth')
        if fanclub_auth_settings is not None:
            return fanclub_auth_settings.get(k)
    return None


def consumer_key_builder(request):
    return get_fanclub_auth_setting(request, u'oauth_consumer_key')


def consumer_secret_builder(request):
    return get_fanclub_auth_setting(request, u'oauth_consumer_secret')