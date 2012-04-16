# -*- coding:utf-8 -*-

"""
nosetestsを実行するとディレクトリをたどる際に辞書順に見ていくらしい。
現在の所、assetが先頭に来るのでここでDBのテーブル作成などしている。
"""
def setUpModule():
    import pyramid.testing as testing
    import sqlahelper
    import sqlalchemy as sa

    config = testing.setUp()
    def non_models_ignore(x):
        return not x.endswith("models")
    config.scan("altaircms", ignore=[non_models_ignore])
    config.scan("altaircms.asset", ignore=[non_models_ignore])
    config.scan("altaircms.page", ignore=[non_models_ignore])
    config.scan("altaircms.tag", ignore=[non_models_ignore])
    
    sqlahelper.add_engine(sa.create_engine("sqlite://"))
    sqlahelper.get_base().metadata.create_all()
    testing.tearDown()

