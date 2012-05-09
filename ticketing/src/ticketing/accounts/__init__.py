# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('accounts.index', '/')
    config.add_route('accounts.new', '/new')
    config.add_route('accounts.show', '/show/{account_id}')
