# coding: utf-8
def includeme(config):
    config.add_route('event', '/event/{id}')
    config.add_route('event_list', '/event/')


    # バックエンドからの受取り用。
    # 認証方式が異なるため独立したインターフェースを設ける。
    config.add_route('api_event_register', '/api/event/register')

    config.add_route('api_event_object', '/api/event/{id}')
    config.add_route('api_event', '/api/event/')
