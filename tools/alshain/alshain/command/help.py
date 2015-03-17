# -*- coding: utf-8 -*-
u"""altair操作のためのユーティリティコマンド

altairの操作は結構typeしないといけないのでユーティリティコマンドを作成してみました。
良かったら使ってみてください。

定義すべき環境変数
=============================

ALTAIR
    altairのソースツリーがあるディレクトリ
    (ex. /srv/altair/currrent)

ALTAIR_DEPLOY
    deploy配下のどの環境をつかうか
    - dev
    - staging
    - qa
    - production

ALTAIR_SUDO
    altairで使用するsudoのuser名

使えるcommand一覧
==============================

次のコマンドを実行してください::

    $ alshain --command-list

"""


def main(argv):
    print __doc__

if __name__ == '__main__':
    main()
