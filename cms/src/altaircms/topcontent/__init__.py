# coding: utf-8

def includeme(config):
    config.add_route('topcontent', '/topcontent/{id}')
    config.add_route('topcontent_delete_confirm', '/topcontent/{id}/delete/confirm')
    config.add_route('topcontent_update_confirm', '/topcontent/{id}/update/confirm')
    config.add_route('topcontent_list', '/topcontent/')

    # バックエンドからの受取り用。
    # 認証方式が異なるため独立したインターフェースを設ける。
    # config.add_route('api_topcontent_register', '/api/topcontent/register')

    config.add_route('api_topcontent_object', '/api/topcontent/{id}')
    config.add_route('api_topcontent', '/api/topcontent/')

    config.scan()
