import xml.etree.ElementTree as et
from .interfaces import ISigner

def generate_requestid():
    """
    安心決済の一意なリクエストIDを生成する
    uuidの前半16桁
    """


def to_xml(checkout):
    root = et.Element(u'orderItemsInfo')
    # snip
    return et.tostring(root)

def sign_hmac_sha1(checkout_xml):
    hashed = hashlib.sha1(checkout_xml).digest()
    return hmac.new(secret).update(hashed).hexdigest()

def sign_hmac_md5(checkout_xml):
    hashed = hashlib.md5(checkout_xml).digest()
    return hmac.new(secret).update(hashed).hexdigest()

def sign_checkout(request, checkout, sign_method):
    signer = request.registry.getUtility(ISigner, name=sign_method)
    return signer(checkout)

AUTH_METHOD_HMAC_SHA1 = 1
AUTH_METHOD_HMAC_MD5 = 2

IS_NOT_TO_MODE = 0
IS_T_MODE = 1

API_STATUS_SUCCESS = 0
API_STATUS_ERROR = 1


ITEM_SETTLEMENT_RESULT_NOT_REQUIRED = 0
ITEM_SETTLEMENT_RESULT_REQUIRED = 1

RESULT_OK = 0
RESULT_ERROR = 1


PAYMENT_STATUS_YET = 0
PAYMENT_STATUS_PROGRESS = 1
PAYMENT_STATUS_COMPLETED = 2

PROCCES_STATUE_PROGRESS = 0
PROCCES_STATUE_COMPLETED = 1

RESULT_FLG_SUCCESS = 0
RESULT_FLG_FAILED = 1


ERROR_CODES = {
    "100": u"メンテナンス中",
    "200": u"システムエラー",
    "300": u"入力値のフォーマットエラー",
    "400": u"サービス ID、アクセスキーのエラー",
    "500": u"リクエスト ID 重複エラー または 実在しないリクエスト ID に対するリクエストエラー",
    "600": u"XML 解析エラー",
    "700": u"全て受付エラー(成功件数が0件)",
    "800": u"最大処理件数エラー(リクエストの処理依頼件数超過)",
}

ORDER_ERROR_CODES = {
    "10", u"設定された注文管理番号が存在しない",
    "11", u"設定された注文管理番号が不正",
    "20", u"􏰀済ステータスが不正",
    "30", u"締め日チェックエラー",
    "40", u"商品 ID が不一致",
    "41", u"商品数が不足",
    "42", u"商品個数が不正(商品個数が 501 以上)",
    "50", u"リクエストの総合計金額が不正(100 円未満)",
    "51", u"リクエストの総合計金額が不正(合計金額が 0 円)",
    "52", u"リクエストの総合計金額が不正(合計金額が 9 桁以上)",
    "60", u"別処理を既に受付(当該データが受付済みで処理待ち)",
    "90", u"システムエラー",
}

ITEM_CONFIRMATION_RESULTS = {
    "0": u"個数・商品単価共に変更なし",
    "1": u"個数変更あり",
    "2": u"商品単価変更あり",
    "3": u"個数・商品単価共に変更あり",
}
