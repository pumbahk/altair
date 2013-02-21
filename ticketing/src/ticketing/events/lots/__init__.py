# -*- coding:utf-8 -*-

def includeme(config):
    
    # 抽選内容管理
    config.add_route('lots.index', '/{event_id}')
    config.add_route('lots.new', '/new/{event_id}')
    config.add_route('lots.show', '/show/{lot_id}')
    config.add_route('lots.edit', '/edit/{lot_id}')

    config.add_route('lots.product_new', '/product_new/{lot_id}')

    # 抽選申し込み管理
    config.add_route('lots.entries.index', 'entries/{lot_id}')
