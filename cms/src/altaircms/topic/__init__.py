# coding: utf-8

def includeme(config):
    # バックエンドからの受取り用。
    # 認証方式が異なるため独立したインターフェースを設ける。
    # config.add_route('api_topic_register', '/api/topic/register')

    config.add_route('api_topic_object', '/api/topic/{id}')
    config.add_route('api_topic', '/api/topic/')

    # config.scan()
