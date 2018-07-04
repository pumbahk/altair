# -*- coding:utf-8 -*-

import urllib
from pyramid.threadlocal import get_current_request
from pyramid.path import AssetResolver
import logging
logger = logging.getLogger(__name__)

## todo: 以下のクラスを利用している箇所のimport文変更
from .modelmanage import (
    ApplicableTicketsProducer, 
    IssuedAtBubblingSetter, 
    PrintedAtBubblingSetter, 
    IssuedPrintedAtSetter, 
)

def tree_dict_from_flatten(d, sep):
    result = {}
    for master_key in d:
        ks = sep(master_key)
        if len(ks) <= 1:
            result[master_key] = d[master_key]
        else:
            target = result
            for k in ks[:-1]:
                if not k in target:
                    target[k] = {}
                target = target[k]
            target[ks[-1]] = d[master_key]
    return result

def merge_dict_recursive(d1, d2): #muttable!. not support list. only atom and dict.
    for k, v in d2.iteritems():
        if not hasattr(v, "iteritems") or not k in d1:
            d1[k] = v
        else:
            sub = d1[k]
            if not hasattr(sub, "iteritems"):
                d1[k] = v
            else:
                merge_dict_recursive(sub, v)
    return d1

class PageURL_WebOb_Ex(object):
    def __init__(self, request, encode_type="utf-8", qualified=False):
        self.request = request
        self.encode_type = encode_type
        self.qualified = qualified

    def __call__(self, page, partial=False):
        if self.qualified:
            path = self.request.application_url
        else:
            path = self.request.path
        return make_page_url(path, self.request.GET, page, self.encode_type, partial)

def make_page_url(path, params, page, encode_type, partial=False):
    params = params.copy()
    params["page"] = page
    if partial:
        params["partial"] = "1"

    qs = urllib.urlencode(dict([k, v.encode(encode_type) if isinstance(v, unicode) else v] for k, v in params.items()))
    return "%s?%s" % (path, qs)


def add_env_label(string, request=None):
    """
    開発・検証環境の場合は文言を追記（TKT-5283）。
    メールの件名など、どの環境で出力された文字列か表示させるために使う。
    使用する文言は各環境の「*.cfg」ファイルで定義されている。
    (例：findable_label.label = stg.altr.jp）

    :param string: 環境名文言を追加する対象の文字列
    :param request: リクエストオブジェクト（なければ生成する）
    :return: 本番環境以外では文字が対象の頭に追記される。
    """
    if not request:
        request = get_current_request()

    environment = request.registry.settings.get('altair.findable_label.label')
    if environment:
        env_label = '[{}]'.format(environment)
        return env_label + string
    else:
        return string


def use_base_dir_if_org_template_not_exists(obj, path, default_package, override_paths=None):
    """
    ORG独自テンプレートが存在していない場合は__base__ディレクトリの同階層ファイルを参照するようにする
    override(dict)で指定。
    """
    organization_short_name = obj.organization_short_name or "__base__"
    package_or_path, colon, _path = path.partition(':')
    if not colon:
        package = default_package
        path = package_or_path
    else:
        package = package_or_path
        path = _path

    if override_paths:
        org_path = override_paths['org_path']
        base_path = override_paths['base_path']
    else:
        # デフォルトで調べるパス
        org_path = '{package}:templates/{organization_short_name}/{ua_type}/{path}'
        base_path = '{package}:templates/__base__/{ua_type}/{path}'

    replace = {
        'package': package,
        'organization_short_name': organization_short_name,
        'ua_type': obj.ua_type,
        'path': path,
    }

    return search_file_from_path_list([org_path, base_path], replace)


def use_base_dir_if_org_static_not_exists(obj, path, module):
    """
    ORG独自の静的コンテンツが存在していない場合は__base__ディレクトリの同階層ファイルを参照するようにする。
    S3側ではなくGit管理下に存在するかを見ていることに注意
    """
    org_path = "altair.app.ticketing.{module}:static/{organization_short_name}/{path}"
    base_path = "altair.app.ticketing.{module}:static/__base__/{path}"
    replace = {
        'organization_short_name': obj.organization_short_name,
        'path': path,
        'module': module
    }

    static_file_path = search_file_from_path_list([org_path, base_path], replace)

    if static_file_path is None:
        # 404ステータスでもシステムの動作に影響ない画像ファイルなどを考慮し、ここではNoneを返さない
        static_file_path = org_path.format(**replace)

    return static_file_path


def search_file_from_path_list(path_list, replace):
    """
    path_listの順にファイルの存在を確認していき、見つかったところでファイルのパスを返す。

    :param path_list: 置換前のパスの文言リスト
    :param replace: 置換するパラメータのdict
    :return: ファイルのパス
    """
    actual_paths = [p.format(**replace) for p in path_list]
    asset = AssetResolver()
    for path in actual_paths:
        if asset.resolve(path).exists():
            return path

    logger.error('could not find "{path}" from {actual_paths}'.format(
        path=replace['path'],
        actual_paths=', '.join(actual_paths)
    ))

    return None
