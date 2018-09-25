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


def search_template_file(obj, path, default_package, override_path_str=None, params=None, log_err=True):
    """
    OrganizationSettingで指定した順にORGテンプレートディレクトリを参照していき、レンダリングに使用するテンプレートファイルを見つける
    引数の名称などは修正前のものを踏襲しているものの分かりづらいため、以下に詳細を明記します。

    :param obj: ViewContextオブジェクト
    :param path: ファイル名
    :param default_package: altair.app.ticketing.cartなどの文字列
    :param override_path_str: 置換元のパス文言（`path_str`）を個別に指定したい場合に指定
    :param params: 置換用の補足パラメータ（dict）
        `login_body`: 会員種別詳細で「ログイン画面の使用」にチェックを入れていると「'__fc_auth__'」の文字列が入ってくる
        `membership`: 会員種別名
        `their_package`: `path_str`に「${their_package}」が使用される場合があり、「altair.app.ticketing.fc_auth」に書き換えるために使われている
    :param log_err: テンプレートファイルが見つからない場合にエラーレベルをERRORで出力するか。FalseであればINFOで出力する。
    :return: テンプレートファイルのパス or None
    """
    package_or_path, colon, _path = path.partition(':')
    if not colon:
        package = default_package
        path = package_or_path
    else:
        package = package_or_path
        path = _path

    default_path_str = u'{package}:templates/{organization_short_name}/{ua_type}/{path}'
    path_str = override_path_str if override_path_str else default_path_str

    rendered_templates = [
        obj.request.organization.setting.rendered_template_1,
        obj.request.organization.setting.rendered_template_2
    ]

    path_list = []
    for rt in rendered_templates:
        if rt != u'-':
            replace = {'package': package, 'organization_short_name': rt, 'ua_type': obj.ua_type, 'path': path}
            if params:
                replace.update(params)
            path_list.append(path_str.format(**replace))

    return check_file_existence_and_return_the_path(path_list, log_err)


def search_static_file(obj, path, module):
    """
    OrganizationSettingで指定した順にORG静的コンテンツディレクトリを参照する。
    S3側ではなくGit管理下に存在を確認 → ファイルが見つかればそのディレクトリをもとにS3のbucketのパスが以降の処理で生成される。
    """
    path_str = u"altair.app.ticketing.{module}:static/{organization_short_name}/{path}"

    rendered_templates = [
        obj.request.organization.setting.rendered_template_1,
        obj.request.organization.setting.rendered_template_2
    ]

    path_list = [path_str.format(
        module=module,
        organization_short_name=rt,
        path=path
    ) for rt in rendered_templates if rt != u'-']

    static_file_path = check_file_existence_and_return_the_path(path_list)

    # ファイルが見つからなくても静的コンテンツのためシステムの動作には影響ない。
    # Noneではなくrendered_template_1で設定されたORGディレクトリのパスを当てておく。
    if static_file_path is None:
        static_file_path = path_list[0]

    return static_file_path


def check_file_existence_and_return_the_path(path_list, log_err=True):
    """
    path_listの順にファイルの存在を確認していき、見つかったところでファイルのパスを返す。

    :param path_list: 置換前のパスの文言リスト
    :param log_err: TrueならログのレベルをERRORで出力する
    :return: ファイルのパス
    """
    asset = AssetResolver()
    for path in path_list:
        if asset.resolve(path).exists():
            return path

    log_str = u'could not find template or static file: "{path_list}"'.format(
        path_list=u', '.join(path_list)
    )

    if log_err:
        logger.warn(log_str)

    return None
