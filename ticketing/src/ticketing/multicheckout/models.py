# -*- coding:utf-8 -*-

""" TBA
"""
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm

from ..models import Identifier

# for schema dependencies
import ticketing.core.models

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

class Secure3DReqEnrolRequest(Base):
    """ 3D認証可否確認依頼処理（リクエスト）
    """
    __tablename__ = 'secure3d_req_enrol_request'
    id = sa.Column(Identifier, primary_key=True)
    CardNumber = sa.Column(sa.Unicode(16), doc="カード番号")
    ExpYear = sa.Column(sa.Unicode(2), doc="カード有効期限(年)")
    ExpMonth = sa.Column(sa.Unicode(2), doc="カード有効期限(月)")
    TotalAmount = sa.Column(sa.Integer, doc="決済金額の総額")
    Currency = sa.Column(sa.Unicode(3), doc="392 を設定 通貨？")

class Secure3DReqEnrolResponse(Base):
    """ 3D認証可否確認依頼処理（レスポンス）
    """
    __tablename__ = 'secure3d_req_enrol_response'
    id = sa.Column(Identifier, primary_key=True)
    Md = sa.Column(sa.UnicodeText, doc="マーチャントデータ")
    ErrorCd = sa.Column(sa.Unicode(6), doc="エラーコード")
    RetCd = sa.Column(sa.Unicode(1), doc="リターンコード")
    AcsUrl = sa.Column(sa.UnicodeText, doc="3D 認証画面を要求するための ACS の URL")
    PaReq = sa.Column(sa.UnicodeText, doc="ACS に送信する電文内容")

    def is_enable_secure3d(self):
        return self.ErrorCd == '000000' and self.RetCd in ('0', '1', '2')

    def is_enable_auth_api(self):
        return self.ErrorCd == '000000' and self.RetCd == '0'

class Secure3DAuthRequest(Base):
    """ 3D認証結果確認依頼処理（リクエスト）
    """
    __tablename__ = 'secure3d_req_auth_request'
    id = sa.Column(Identifier, primary_key=True)
    Md = sa.Column(sa.UnicodeText, doc="マーチャントデータ")
    PaRes = sa.Column(sa.UnicodeText, doc="PARes 電文")


class Secure3DAuthResponse(Base):
    """ 3D認証結果確認依頼処理（リクエスト）
    """
    __tablename__ = 'secure3d_req_auth_response'
    id = sa.Column(Identifier, primary_key=True)

    ErrorCd = sa.Column(sa.Unicode(6), doc="エラーコート")
    RetCd = sa.Column(sa.Unicode(1), doc="リターンコート")
    Xid = sa.Column(sa.Unicode(28), doc="トランザクションID")
    Ts = sa.Column(sa.Unicode(1), doc="トランザクションステータス")
    Cavva = sa.Column(sa.Unicode(1), doc="CAVV アルゴリズム")
    Cavv = sa.Column(sa.Unicode(28), doc="CAVV")
    Eci = sa.Column(sa.Unicode(2), doc="ECI")
    Mvn = sa.Column(sa.Unicode(10), doc="メッセージバージョンナンバー")

    def is_enable_secure3d(self):
        return self.ErrorCd == '000000' and self.RetCd in ('0', '1', '2')

    def is_enable_auth_checkout(self):
        return self.ErrorCd == '000000' and self.RetCd == '0'

class MultiCheckoutRequestCard(Base):
    """

    セキュリティ区分

    - 1: 認証無し SSL
    - 2: セキュリティコード CVV
    - 3: 3Dセキュア 3D
    """
    __tablename__ = 'multicheckout_request_card'
    id = sa.Column(Identifier, primary_key=True)

    query = DBSession.query_property()

    #order

    ItemCd = sa.Column(sa.Unicode(3), doc=u"注文コード")
    ItemName = sa.Column(sa.Unicode(44), doc=u"商品名") # 44バイト...
    OrderYMD = sa.Column(sa.Unicode(8), doc=u"注文年月日（当日以前）") # YYYYMMDD
    SalesAmount = sa.Column(sa.Integer, doc=u"売上金額")
    TaxCarriage = sa.Column(sa.Integer, doc=u"税送料")
    FreeData = sa.Column(sa.Unicode(32), doc=u"任意設定項目") # 32バイト...
    ClientName = sa.Column(sa.Unicode(40), doc=u"購入者名")
    MailAddress = sa.Column(sa.Unicode(100), doc=u"購入者メールアドレス")
    MailSend = sa.Column(sa.Unicode(1), doc=u"メール送信フラグ")

    # card
    CardNo = sa.Column(sa.Unicode(16), doc=u"カード番号")
    CardLimit = sa.Column(sa.Unicode(4), doc=u"カード有効期限")
    CardHolderName = sa.Column(sa.Unicode(42), doc=u"カード名義人")
    PayKindCd = sa.Column(sa.Unicode(2), doc=u"支払区分コード")
    PayCount = sa.Column(sa.Integer, doc=u"支払回数")
    SecureKind = sa.Column(sa.Unicode(1), doc=u"セキュリティ方式")


    # Secure Code
    SecureCode = sa.Column(sa.Unicode(4), doc=u"セキュリティコード")

    # 3DSecure

    Mvn = sa.Column(sa.Unicode(10), doc=u"メッセージバージョンナンバ")
    Xid = sa.Column(sa.Unicode(28), doc=u"トランザクションID")
    Ts = sa.Column(sa.Unicode(1), doc=u"トランザクションステータス")
    ECI = sa.Column(sa.Unicode(2), doc=u"ECI")
    CAVV = sa.Column(sa.Unicode(28), doc=u"CAVV")
    CavvAlgorithm = sa.Column(sa.Unicode(1), doc=u"CAVVアルゴリズム")

class MultiCheckoutResponseCard(Base):
    __tablename__ = 'multicheckout_response_card'
    id = sa.Column(Identifier, primary_key=True)

    #依頼情報
    BizClassCd = sa.Column(sa.Unicode(2), doc=u"業務分類コード")
    Storecd = sa.Column(sa.Unicode(10), doc=u"店舗コード")

    #結果情報
    OrderNo = sa.Column(sa.Unicode(32), doc=u"受注番号")
    Status = sa.Column(sa.Unicode(3), doc=u"決済ステータス")
    PublicTranId = sa.Column(sa.Unicode(25), doc=u"トランザクションID")
    AheadComCd = sa.Column(sa.Unicode(7), doc=u"仕向先会社コード")
    ApprovalNo = sa.Column(sa.Unicode(7), doc=u"承認番号")
    CardErrorCd = sa.Column(sa.Unicode(6), doc=u"カード決済詳細エラーコード")
    ReqYmd = sa.Column(sa.Unicode(8), doc=u"依頼年月日(YYYYMMDD)")
    CmnErrorCd = sa.Column(sa.Unicode(6), doc=u"共通エラーコード")


class MultiCheckoutInquiryResponseCardHistory(Base):
    """ 取引照会レスポンス履歴情報
    """

    __tablename__ = 'multicheckout_inquiry_response_card_history'
    id = sa.Column(Identifier, primary_key=True)

    BizClassCd = sa.Column(sa.Unicode(2), doc=u"業務分類コード")
    EventDate = sa.Column(sa.Unicode(14), doc=u"取引日時(yyyymmddhhmiss)")
    SalesAmount = sa.Column(sa.Unicode(7), doc=u"売上金額")

    inquiry_id = sa.Column(Identifier, sa.ForeignKey("multicheckout_inquiry_response_card.id"))
    inquiry = orm.relationship(
        "MultiCheckoutInquiryResponseCard",
        backref="histories")


class MultiCheckoutInquiryResponseCard(Base):
    """ 取引照会レスポンス
    """

    __tablename__ = 'multicheckout_inquiry_response_card'
    id = sa.Column(Identifier, primary_key=True)

    Storecd = sa.Column(sa.Unicode(10), doc=u"店舗コード")

    #基本情報
    EventDate = sa.Column(sa.Unicode(14), doc=u"取引日時(yyyymmddhhmiss)")
    Status = sa.Column(sa.Unicode(3), doc=u"決済ステータス")
    CardErrorCd = sa.Column(sa.Unicode(6), doc=u"カード決済詳細エラーコード")
    ApprovalNo = sa.Column(sa.Unicode(7), doc=u"承認番号")
    CmnErrorCd = sa.Column(sa.Unicode(6), doc=u"共通エラーコード")

    #注文情報
    OrderNo = sa.Column(sa.Unicode(32), doc=u"受注番号")
    ItemName = sa.Column(sa.Unicode(44), doc=u"商品名") # 44バイト...
    OrderYMD = sa.Column(sa.Unicode(8), doc=u"注文年月日（当日以前）") # YYYYMMDD
    SalesAmount = sa.Column(sa.Integer, doc=u"売上金額")
    FreeData = sa.Column(sa.Unicode(32), doc=u"任意設定項目") # 32バイト...

    #購入者情報
    ClientName = sa.Column(sa.Unicode(40), doc=u"購入者名")
    MailAddress = sa.Column(sa.Unicode(100), doc=u"購入者メールアドレス")
    MailSend = sa.Column(sa.Unicode(1), doc=u"メール送信フラグ")

    #カード情報
    CardNo = sa.Column(sa.Unicode(16), doc=u"カード番号")
    CardLimit = sa.Column(sa.Unicode(4), doc=u"カード有効期限")
    CardHolderName = sa.Column(sa.Unicode(42), doc=u"カード名義人")
    PayKindCd = sa.Column(sa.Unicode(2), doc=u"支払区分コード")
    PayCount = sa.Column(sa.Integer, doc=u"支払回数")
    SecureKind = sa.Column(sa.Unicode(1), doc=u"セキュリティ方式")

    #履歴情報 : MultiCheckoutInquiryResponseCardHistory
