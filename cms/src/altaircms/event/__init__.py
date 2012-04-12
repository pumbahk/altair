# coding: utf-8
from .interfaces import IAPIKEYValidator, IEventRepositiry

def includeme(config):
    config.add_route('event', '/event/{id}')
    config.add_route('event_list', '/event/')


    # バックエンドからの受取り用。
    # 認証方式が異なるため独立したインターフェースを設ける。
    config.add_route('api_event_register', '/api/event/register')

    config.add_route('api_event_object', '/api/event/{id}')
    config.add_route('api_event', '/api/event/')

    reg = config.registry
    validate_apikey = config.maybe_dotted('.api.validate_apikey')
    reg.registerUtility(validate_apikey, IAPIKEYValidator)
    event_repository = config.maybe_dotted('.api.EventRepositry')
    reg.registerUtility(event_repository, IEventRepositiry)

    config.scan()
