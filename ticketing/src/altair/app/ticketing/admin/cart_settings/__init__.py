# encoding: utf-8

cart_setting_types = [
    (u'standard', u'標準'),
    (u'fc', u'入会フォーム'),
    (u'lot', u'抽選フォーム'),
    (u'goods', u'グッズ販売フォーム'),
    (u'passport', u'パスポートフォーム')
    ]


CART_SETTING_TYPE_STANDARD = u'standard'


def setup__views(config):
    config.add_route('cart_setting.visible', '/visible')
    config.add_route('cart_setting.invisible', '/invisible')
    config.add_route('cart_setting.index', '/', factory='.resources.CartSettingListResource')
    config.add_route('cart_setting.new', '/new', factory='.resources.CartSettingListResource')
    config.add_route('cart_setting.show', '/{cart_setting_id}', factory='.resources.CartSettingResource')
    config.add_route('cart_setting.edit', '/{cart_setting_id}/edit', factory='.resources.CartSettingResource')

def includeme(config):
    config.include(setup__views, route_prefix='/cart_settings')
    config.scan('.views')
