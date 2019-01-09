# -*- coding: utf-8 -*-


def includeme(config):
    # パスポート設定
    config.add_route('passport.index', '/', factory='.resources.PassportResource')
    config.add_route('passport.show', '/show/{passport_id}', factory='.resources.PassportResource')
    config.add_route('passport.new', '/new', factory='.resources.PassportResource')
    config.add_route('passport.edit', '/edit/{passport_id}', factory='.resources.PassportResource')
    config.add_route('passport.delete', '/delete/{passport_id}', factory='.resources.PassportResource')
    # 入場不可期間設定
    config.add_route('term.index', '/term/{passport_id}', factory='.resources.PassportResource')
    config.add_route('term.new', '/term/{passport_id}/new', factory='.resources.PassportResource')
    config.add_route('term.show', '/term/show/{term_id}', factory='.resources.PassportResource')
    config.add_route('term.edit', '/term/edit/{term_id}', factory='.resources.PassportResource')
    config.add_route('term.delete', '/term/delete/{term_id}', factory='.resources.PassportResource')
    # パスポートユーザ一覧
    config.add_route('passport.users.index', '/users', factory='.resources.PassportResource')
    config.add_route('passport.user.download', '/user/download/{passport_user_id}',
                     factory='.resources.PassportResource')
    config.scan(".")
