# -*- coding:utf-8 -*-

""" TBA
"""
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm

# for schema dependencies
import ticketing.venues.models
import ticketing.orders.models
import ticketing.events.models

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()


class MultiCheckoutRequestCard(Base):
    __tablename__ = 'multicheckout_request_card'
    id = sa.Column(sa.Integer, primary_key=True)

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
    id = sa.Column(sa.Integer, primary_key=True)

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
    id = sa.Column(sa.Integer, primary_key=True)

    BizClassCd = sa.Column(sa.Unicode(2), doc=u"業務分類コード")
    EventDate = sa.Column(sa.Unicode(14), doc=u"取引日時(yyyymmddhhmiss)")
    SalesAmount = sa.Column(sa.Unicode(7), doc=u"売上金額")

    inquiry_id = sa.Column(sa.Integer, sa.ForeignKey("multicheckout_inquiry_response_card.id"))
    inquiry = orm.relationship(
        "MultiCheckoutInquiryResponseCard",
        backref="histories")


class MultiCheckoutInquiryResponseCard(Base):
    """ 取引照会レスポンス
    """

    __tablename__ = 'multicheckout_inquiry_response_card'
    id = sa.Column(sa.Integer, primary_key=True)

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