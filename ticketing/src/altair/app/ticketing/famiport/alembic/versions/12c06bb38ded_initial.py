# encoding: utf-8
"""initial

Revision ID: 12c06bb38ded
Revises: None
Create Date: 2015-06-10 03:39:59.404088

"""

# revision identifiers, used by Alembic.
revision = '12c06bb38ded'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    from altair.app.ticketing.famiport.models import FamiPortSalesChannel, FamiPortPerformanceType, FamiPortTicketType, FamiPortRefundType, MutableSpaceDelimitedList, SpaceDelimitedList, FamiPortOrderType  # noqa
    op.create_table(
        'FamiPortBarcodeNoSequence',
        sa.Column('id', Identifier, autoincrement=True, primary_key=True),
        )
    op.create_table(
        'FamiPortOrderIdentifierSequence',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('prefix', sa.Unicode(3), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortOrderTicketNoSequence',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('value', sa.String(13), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortExchangeTicketNoSequence',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('value', sa.String(13), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortReserveNumberSequence',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('value', sa.String(13), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPlayguide',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('name', sa.Unicode(50), nullable=False),
        sa.Column('discrimination_code', sa.Integer, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortClient',
        sa.Column('famiport_playguide_id', Identifier, sa.ForeignKey('FamiPortPlayguide.id'), nullable=False),
        sa.Column('code', sa.Unicode(24), nullable=False, primary_key=True),
        sa.Column('name', sa.Unicode(50), nullable=False),
        sa.Column('prefix', sa.Unicode(3), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortGenre1',
        sa.Column('code', sa.Unicode(23), primary_key=True),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortGenre2',
        sa.Column('code', sa.Unicode(35), primary_key=True),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortVenue',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('name', sa.Unicode(50), nullable=False),
        sa.Column('name_kana', sa.Unicode(200), nullable=False),
        sa.Column('prefecture', sa.Integer, nullable=False, server_default=text(u"0")),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortEvent',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('userside_id', Identifier, nullable=True, index=True),
        sa.Column('code_1', sa.Unicode(6), nullable=False),
        sa.Column('code_2', sa.Unicode(4), nullable=False),
        sa.Column('name_1', sa.Unicode(80), nullable=False, server_default=text(u'""')),
        sa.Column('name_2', sa.Unicode(80), nullable=False, server_default=text(u'""')),
        sa.Column('sales_channel', sa.Integer, nullable=False, server_default=text(unicode(FamiPortSalesChannel.FamiPortOnly.value))),
        sa.Column('client_code', sa.Unicode(24), sa.ForeignKey('FamiPortClient.code')),
        sa.Column('venue_id', Identifier, sa.ForeignKey('FamiPortVenue.id')),
        sa.Column('purchasable_prefectures', MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(137))),
        sa.Column('start_at', sa.DateTime(), nullable=True),
        sa.Column('end_at', sa.DateTime(), nullable=True),
        sa.Column('genre_1_code', sa.Unicode(23), sa.ForeignKey('FamiPortGenre1.code')),
        sa.Column('genre_2_code', sa.Unicode(35), sa.ForeignKey('FamiPortGenre2.code')),
        sa.Column('keywords', MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(30000).adapt(sa.UnicodeText))),
        sa.Column('search_code', sa.Unicode(20)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortPerformance',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('userside_id', Identifier, nullable=True, index=True),
        sa.Column('famiport_event_id', Identifier, sa.ForeignKey('FamiPortEvent.id'), nullable=False),
        sa.Column('code', sa.Unicode(3)),
        sa.Column('name', sa.Unicode(60)),
        sa.Column('type', sa.Integer, nullable=False, server_default=text(unicode(FamiPortPerformanceType.Normal.value))),
        sa.Column('searchable', sa.Boolean, nullable=False, server_default=text(u"TRUE")),
        sa.Column('sales_channel', sa.Integer, nullable=False, server_default=text(unicode(FamiPortSalesChannel.FamiPortOnly.value))),
        sa.Column('start_at', sa.DateTime(), nullable=True),
        sa.Column('ticket_name', sa.Unicode(20), nullable=True),  # only valid if type = Spanned
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortSalesSegment',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('userside_id', Identifier, nullable=True, index=True),
        sa.Column('famiport_performance_id',  Identifier, sa.ForeignKey('FamiPortPerformance.id'), nullable=False),
        sa.Column('code', sa.Unicode(3), nullable=False),
        sa.Column('name', sa.Unicode(40), nullable=False),
        sa.Column('sales_channel', sa.Integer, nullable=False, server_default=text(unicode(FamiPortSalesChannel.FamiPortOnly.value))),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('start_at', sa.DateTime(), nullable=False),
        sa.Column('end_at', sa.DateTime(), nullable=True),
        sa.Column('auth_required', sa.Boolean, nullable=False, server_default=text(u"FALSE")),
        sa.Column('auth_message', sa.Unicode(320), nullable=False, server_default=text(u"''")),
        sa.Column('seat_selection_start_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortOrder',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('type', sa.Integer, nullable=False),
        sa.Column('shop_code', sa.Unicode(7), nullable=True),
        sa.Column('order_no', sa.Unicode(255), nullable=False),  # altair側予約番号
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.Column('client_code', sa.Unicode(24), sa.ForeignKey('FamiPortClient.code'), nullable=False),
        sa.Column('famiport_sales_segment_id', Identifier, sa.ForeignKey('FamiPortSalesSegment.id'), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=16, scale=0), nullable=False),
        sa.Column('ticket_payment', sa.Numeric(precision=16, scale=0), nullable=False),
        sa.Column('system_fee', sa.Numeric(precision=16, scale=0), nullable=False),
        sa.Column('ticketing_fee', sa.Numeric(precision=16, scale=0), nullable=False),
        sa.Column('famiport_order_identifier', sa.String(12), nullable=False),
        sa.Column('reserve_number', sa.String(13), nullable=False),
        sa.Column('customer_name_input', sa.Boolean, nullable=False, server_default=text('FALSE')),
        sa.Column('customer_name', sa.Unicode(42), nullable=False),
        sa.Column('customer_phone_input', sa.Boolean, nullable=False, server_default=text('FALSE')),
        sa.Column('customer_phone_number', sa.Unicode(12), nullable=False, server_default=text("''")),
        sa.Column('ticketing_start_at', sa.DateTime(), nullable=True),
        sa.Column('ticketing_end_at', sa.DateTime(), nullable=True),
        sa.Column('payment_start_at', sa.DateTime(), nullable=True),
        sa.Column('payment_due_at', sa.DateTime(), nullable=True),
        sa.Column('customer_name', sa.Unicode(42), nullable=False),  # 氏名
        sa.Column('customer_name_input', sa.Boolean, nullable=False, server_default=text(u"FALSE")),  # 氏名要求フラグ
        sa.Column('customer_phone_input', sa.Boolean, nullable=False, server_default=text(u"FALSE")),  # 電話番号要求フラグ
        sa.Column('customer_address_1', sa.Unicode(200), nullable=False, server_default=text(u"''")),  # 住所1
        sa.Column('customer_address_2', sa.Unicode(200), nullable=False, server_default=text(u"''")),  # 住所2
        sa.Column('customer_phone_number', sa.Unicode(12), nullable=False),  # 電話番号
        sa.Column('paid_at', sa.DateTime(), nullable=True),  # 支払日時
        sa.Column('issued_at', sa.DateTime(), nullable=True),  # 発券日時
        sa.Column('canceled_at', sa.DateTime(), nullable=True),  # キャンセル日時
        sa.Column('cancel_reason', sa.Integer, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('invalidated_at', sa.DateTime, nullable=True),
        sa.Column('generation', sa.Integer, nullable=False, server_default=text(u"0")),
        sa.Column('report_generated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortTicket',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('famiport_order_id', Identifier, sa.ForeignKey('FamiPortOrder.id'), nullable=False),
        sa.Column('type', sa.Integer, nullable=False, server_default=text(unicode(FamiPortTicketType.TicketWithBarcode.value))),
        sa.Column('barcode_number', sa.Unicode(13), nullable=False),
        sa.Column('template_code', sa.Unicode(10), nullable=False),
        sa.Column('data', sa.Unicode(4000), nullable=False),
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortRefund',
        sa.Column('id', Identifier, nullable=False, primary_key=True, autoincrement=True),
        sa.Column('type', sa.Integer, nullable=False, server_default=text(unicode(FamiPortRefundType.Type1.value))),
        sa.Column('send_back_due_at', sa.Date(), nullable=False),
        sa.Column('start_at', sa.DateTime(), nullable=False),
        sa.Column('end_at', sa.DateTime(), nullable=False),
        sa.Column('last_serial', sa.Integer, nullable=False, server_default=text(u"FALSE")),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortRefundEntry',
        sa.Column('id',                    Identifier, primary_key=True, autoincrement=True),
        sa.Column('famiport_refund_id',    Identifier, sa.ForeignKey('FamiPortRefund.id'), nullable=False),
        sa.Column('serial',                sa.Integer, nullable=False, server_default=text(u"0")),
        sa.Column('famiport_ticket_id',    Identifier, sa.ForeignKey('FamiPortTicket.id'), nullable=False),
        sa.Column('ticket_payment',        sa.Numeric(precision=9, scale=0)),
        sa.Column('ticketing_fee',         sa.Numeric(precision=8, scale=0)),
        sa.Column('system_fee',            sa.Numeric(precision=8, scale=0)),
        sa.Column('other_fees',            sa.Numeric(precision=8, scale=0)),
        sa.Column('shop_code',             sa.Unicode(7), nullable=False),
        sa.Column('refunded_at',           sa.DateTime(), nullable=True),
        sa.Column('report_generated_at',   sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortInformationMessage',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('result_code', sa.Enum('WithInformation', 'ServiceUnavailable'), unique=True, nullable=False),  # 案内処理結果コード名
        sa.Column('message', sa.Unicode(1000), nullable=False),  # 案内文言
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table(
        'FamiPortReservationInquiryRequest',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('storeCode', sa.Unicode(6), nullable=False),  # 店舗コード
        sa.Column('ticketingDate', sa.Unicode(14), nullable=False),  # 利用日時
        sa.Column('reserveNumber', sa.Unicode(13), nullable=False),  # 予約番号
        sa.Column('authNumber', sa.Unicode(13), nullable=False),  # 認証番号
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )

    op.create_table(
        'FamiPortPaymentTicketingRequest',
        sa.Column('id', Identifier),
        sa.Column('storeCode', sa.Unicode(6), nullable=False),  # 店舗コード
        sa.Column('mmkNo', sa.Unicode(1), nullable=False),  # 発券ファミポート番号
        sa.Column('ticketingDate', sa.Unicode(14), nullable=False),  # 利用日時
        sa.Column('sequenceNo', sa.Unicode(11), nullable=False),  # 処理通番
        sa.Column('playGuideId', sa.Unicode(24), nullable=False),  # クライアントID
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False),  # 支払番号
        sa.Column('customerName', sa.Unicode(42), nullable=False),  # カナ氏名
        sa.Column('phoneNumber', sa.Unicode(11), nullable=False),  # 電話番号
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingCompletionRequest',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('storeCode', sa.Unicode(6), nullable=False),  # 店舗コード
        sa.Column('mmkNo', sa.Unicode(1), nullable=False),  # 発券ファミポート番号
        sa.Column('ticketingDate', sa.Unicode(14), nullable=False),  # 利用日時
        sa.Column('sequenceNo', sa.Unicode(11), nullable=False),  # 処理通番
        sa.Column('requestClass', sa.Unicode(2), nullable=False),  # 要求区分 TODO Delete the field?
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False),  # 支払番号
        sa.Column('playGuideId', sa.Unicode(24), nullable=False),  # クライアントID
        sa.Column('orderId', sa.Unicode(12), nullable=False),  # 注文ID
        sa.Column('totalAmount', sa.Unicode(8), nullable=False),  # 入金金額
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingCancelRequest',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('storeCode', sa.Unicode(6), nullable=False),  # 店舗コード
        sa.Column('mmkNo', sa.Unicode(1), nullable=False),  # 発券ファミポート番号
        sa.Column('ticketingDate', sa.Unicode(14), nullable=False),  # 利用日時
        sa.Column('sequenceNo', sa.Unicode(11), nullable=False),  # 処理通番
        sa.Column('requestClass', sa.Unicode(2), nullable=False),  # 要求区分 TODO Delete the field?
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False),  # 支払番号
        sa.Column('playGuideId', sa.Unicode(24), nullable=False),  # クライアントID
        sa.Column('orderId', sa.Unicode(12), nullable=False),  # 注文ID
        sa.Column('cancelCode', sa.Unicode(2), nullable=False),  # 取消理由
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortInformationRequest',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('infoKubun', sa.Unicode(1), nullable=False),  # 案内種別
        sa.Column('storeCode', sa.Unicode(6), nullable=False),  # 店舗コード
        sa.Column('kogyoCode', sa.Unicode(6), nullable=False),  # 興行コード
        sa.Column('kogyoSubCode', sa.Unicode(4), nullable=False),  # 興行サブコード
        sa.Column('koenCode', sa.Unicode(3), nullable=False),  # 公演コード
        sa.Column('uketsukeCode', sa.Unicode(3), nullable=False),  # 受付コード
        sa.Column('playGuideId', sa.Unicode(24), nullable=False),  # クライアントID
        sa.Column('authCode', sa.Unicode(100), nullable=False),  # 認証コード
        sa.Column('reserveNumber', sa.Unicode(13), nullable=False),  # 予約照会番号
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortCustomerInformationRequest',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('storeCode', sa.Unicode(6), nullable=False),  # 店舗コード
        sa.Column('mmkNo', sa.Unicode(1), nullable=False),  # 発券Famiポート番号
        sa.Column('ticketingDate', sa.Unicode(14), nullable=False),  # 利用日時
        sa.Column('sequenceNo', sa.Unicode(11), nullable=False),  # 処理通番
        sa.Column('requestClass', sa.Unicode(2), nullable=False),  # 要求区分 TODO Delete the field?
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False),  # バーコード情報
        sa.Column('playGuideId', sa.Unicode(24), nullable=False),  # クライアントID
        sa.Column('orderId', sa.Unicode(12), nullable=False),  # 注文ID
        sa.Column('totalAmount', sa.Unicode(8), nullable=False),  # 入金金額
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortRefundEntryRequest',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('businessFlg', sa.Unicode(1)),
        sa.Column('textTyp', sa.Unicode(1)),
        sa.Column('entryTyp', sa.Unicode(1)),
        sa.Column('shopNo', sa.Unicode(7)),
        sa.Column('registerNo', sa.Unicode(2)),
        sa.Column('timeStamp', sa.Unicode(8)),
        sa.Column('barCode1', sa.Unicode(13)),
        sa.Column('barCode2', sa.Unicode(13)),
        sa.Column('barCode3', sa.Unicode(13)),
        sa.Column('barCode4', sa.Unicode(13)),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp())
        )
    op.create_table(
        'FamiPortReservationInquiryResponse',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('resultCode', sa.Unicode(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('replyClass', sa.Unicode(1), nullable=False, server_default=''),  # 応答結果区分
        sa.Column('replyCode', sa.Unicode(2), nullable=False, server_default=''),  # 応答結果
        sa.Column('playGuideId', sa.Unicode(24), nullable=False, server_default=''),  # クライアントID
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False, server_default=''),  # チケットバーコード番号
        sa.Column('totalAmount', sa.Unicode(8), nullable=False, server_default=''),  # 合計金額
        sa.Column('ticketPayment', sa.Unicode(8), nullable=False, server_default=''),  # チケット料金
        sa.Column('systemFee', sa.Unicode(8), nullable=False, server_default=''),  # システム利用料
        sa.Column('ticketingFee', sa.Unicode(8), nullable=False, server_default=''),  # チケット料金
        sa.Column('ticketCountTotal', sa.Unicode(8), nullable=False, server_default=''),  # チケット枚数
        sa.Column('ticketCount', sa.Unicode(8), nullable=False, server_default=''),  # 本券購入枚数
        sa.Column('kogyoName', sa.Unicode(40), nullable=False, server_default=''),  # 興行名
        sa.Column('koenDate', sa.Unicode(12), nullable=False, server_default=''),  # 公演日時
        sa.Column('name', sa.Unicode(42), nullable=False, server_default=''),  # お客様指名
        sa.Column('nameInput', sa.Unicode(1), nullable=False, server_default=''),  # 氏名要求フラグ
        sa.Column('phoneInput', sa.Unicode(1), nullable=False, server_default=''),  # 電話番号要求フラグ
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingResponse',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('resultCode', sa.Unicode(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('storeCode', sa.Unicode(6), nullable=False, server_default=''),  # 店舗コード
        sa.Column('sequenceNo', sa.Unicode(11), nullable=False, server_default=''),  # 処理通番
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False, server_default=''),  # 支払番号
        sa.Column('orderId', sa.Unicode(12), nullable=False, server_default=''),  # 注文ID
        sa.Column('replyClass', sa.Unicode(1), nullable=False, server_default=''),  # 応答結果区分
        sa.Column('replyCode', sa.Unicode(2), nullable=False, server_default=''),  # 応答結果
        sa.Column('playGuideId', sa.Unicode(24), nullable=False, server_default=''),  # クライアントID
        sa.Column('playGuideName', sa.Unicode(50), nullable=False, server_default=''),  # クライアント漢字名称
        sa.Column('orderTicketNo', sa.Unicode(13), nullable=False, server_default=''),  # 払込票番号
        sa.Column('exchangeTicketNo', sa.Unicode(13), nullable=False, server_default=''),  # 引換票番号
        sa.Column('ticketingStart', sa.Unicode(12), nullable=False, server_default=''),  # 発券開始日時
        sa.Column('ticketingEnd', sa.Unicode(12), nullable=False, server_default=''),  # 発券期限日時
        sa.Column('totalAmount', sa.Unicode(8), nullable=False, server_default=''),  # 合計金額
        sa.Column('ticketPayment', sa.Unicode(8), nullable=False, server_default=''),  # チケット料金
        sa.Column('systemFee', sa.Unicode(8), nullable=False, server_default=''),  # システム利用料
        sa.Column('ticketingFee', sa.Unicode(8), nullable=False, server_default=''),  # 店頭発券手数料
        sa.Column('ticketCountTotal', sa.Unicode(2), nullable=False, server_default=''),  # チケット枚数
        sa.Column('ticketCount', sa.Unicode(2), nullable=False, server_default=''),  # 本券購入枚数
        sa.Column('kogyoName', sa.Unicode(40), nullable=False, server_default=''),  # 興行名
        sa.Column('koenDate', sa.Unicode(12), nullable=False, server_default=''),  # 公演日時
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False, server_default=''),  # チケットバーコード番号
        sa.Column('ticketClass', sa.Unicode(1), nullable=False, server_default=''),  # チケット区分
        sa.Column('templateCode', sa.Unicode(10), nullable=False, server_default=''),  # テンプレートコード
        sa.Column('ticketData', sa.Unicode(4000), nullable=False, server_default=''),  # 券面データ
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingCompletionResponse',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('resultCode', sa.Unicode(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('storeCode', sa.Unicode(6), nullable=False, server_default=''),  # 店舗コード
        sa.Column('sequenceNo', sa.Unicode(11), nullable=False, server_default=''),  # 処理通番
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False, server_default=''),  # 支払番号
        sa.Column('orderId', sa.Unicode(12), nullable=False, server_default=''),  # 注文ID
        sa.Column('replyCode', sa.Unicode(2), nullable=False, server_default=''),  # 応答結果
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingCancelResponse',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('resultCode', sa.Unicode(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('storeCode', sa.Unicode(6), nullable=False, server_default=''),  # 店舗コード
        sa.Column('sequenceNo', sa.Unicode(11), nullable=False, server_default=''),  # 処理通番
        sa.Column('barCodeNo', sa.Unicode(13), nullable=False, server_default=''),  # 支払番号
        sa.Column('orderId', sa.Unicode(12), nullable=False, server_default=''),  # 注文ID
        sa.Column('replyCode', sa.Unicode(2), nullable=False, server_default=''),  # 応答結果
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortInformationResponse',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('resultCode', sa.Unicode(2), nullable=False, server_default=''),  # 処理結果コード
        sa.Column('infoKubu', sa.Unicode(1), nullable=False, server_default=''),  # 案内区分
        sa.Column('infoMessage', sa.Unicode(500), nullable=False, server_default=''),  # 案内文言
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortCustomerInformationResponse',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('resultCode', sa.Unicode(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('replyCode', sa.Unicode(2), nullable=False, server_default=''),  # 応答結果
        sa.Column('name', sa.Unicode(42), nullable=False, server_default=''),  # 氏名
        sa.Column('memberId', sa.Unicode(100), nullable=False, server_default=''),  # 会員ID
        sa.Column('address1', sa.Unicode(200), nullable=False, server_default=''),  # 住所1
        sa.Column('address2', sa.Unicode(200), nullable=False, server_default=''),  # 住所1
        sa.Column('identifyNo', sa.Unicode(16), nullable=False, server_default=''),  # 半券個人識別番号
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortTicketResponse',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('famiport_payment_ticketing_response_id', Identifier, sa.ForeignKey('FamiPortPaymentTicketingResponse.id')),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortRefundEntryResponse',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('businessFlg', sa.Unicode(1)),
        sa.Column('textTyp', sa.Unicode(1)),
        sa.Column('entryTyp', sa.Unicode(1)),
        sa.Column('shopNo', sa.Unicode(7)),
        sa.Column('registerNo', sa.Unicode(2)),
        sa.Column('timeStamp', sa.Unicode(8)),
        sa.Column('barCode1', sa.Unicode(13)),
        sa.Column('resultCode1', sa.Unicode(2)),
        sa.Column('mainTitle1', sa.Unicode(30)),
        sa.Column('perfDay1', sa.Unicode(8)),
        sa.Column('repayment1', sa.Unicode(6)),
        sa.Column('refundStart1', sa.Unicode(8)),
        sa.Column('refundEnd1', sa.Unicode(8)),
        sa.Column('ticketTyp1', sa.Unicode(1)),
        sa.Column('charge1', sa.Unicode(6)),
        sa.Column('barCode2', sa.Unicode(13)),
        sa.Column('resultCode2', sa.Unicode(2)),
        sa.Column('mainTitle2', sa.Unicode(30)),
        sa.Column('perfDay2', sa.Unicode(8)),
        sa.Column('repayment2', sa.Unicode(6)),
        sa.Column('refundStart2', sa.Unicode(8)),
        sa.Column('refundEnd2', sa.Unicode(8)),
        sa.Column('ticketTyp2', sa.Unicode(1)),
        sa.Column('charge2', sa.Unicode(6)),
        sa.Column('barCode3', sa.Unicode(13)),
        sa.Column('resultCode3', sa.Unicode(2)),
        sa.Column('mainTitle3', sa.Unicode(30)),
        sa.Column('perfDay3', sa.Unicode(8)),
        sa.Column('repayment3', sa.Unicode(6)),
        sa.Column('refundStart3', sa.Unicode(8)),
        sa.Column('refundEnd3', sa.Unicode(8)),
        sa.Column('ticketTyp3', sa.Unicode(1)),
        sa.Column('charge3', sa.Unicode(6)),
        sa.Column('barCode4', sa.Unicode(13)),
        sa.Column('resultCode4', sa.Unicode(2)),
        sa.Column('mainTitle4', sa.Unicode(30)),
        sa.Column('perfDay4', sa.Unicode(8)),
        sa.Column('repayment4', sa.Unicode(6)),
        sa.Column('refundStart4', sa.Unicode(8)),
        sa.Column('refundEnd4', sa.Unicode(8)),
        sa.Column('ticketTyp4', sa.Unicode(1)),
        sa.Column('charge4', sa.Unicode(6)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False)
        )
    op.create_table(
        'FamiPortShop',
        sa.Column('id', Identifier, primary_key=True, autoincrement=True),
        sa.Column('code', sa.Unicode(5), nullable=False, unique=True),
        sa.Column('company_code', sa.Unicode(4), nullable=False),
        sa.Column('company_name', sa.Unicode(40), nullable=False),
        sa.Column('district_code', sa.Unicode(1), nullable=False),
        sa.Column('district_name', sa.Unicode(40), nullable=False),
        sa.Column('district_valid_from', sa.Date(), nullable=False),
        sa.Column('branch_code', sa.Unicode(3), nullable=False),
        sa.Column('branch_name', sa.Unicode(40), nullable=False),
        sa.Column('branch_valid_from', sa.Date(), nullable=False),
        sa.Column('name', sa.Unicode(30), nullable=False),
        sa.Column('name_kana', sa.Unicode(60), nullable=False),
        sa.Column('tel', sa.Unicode(12), nullable=False),
        sa.Column('prefecture', sa.Integer(), nullable=False),
        sa.Column('prefecture_name', sa.Unicode(20), nullable=False),
        sa.Column('address', sa.Unicode(80), nullable=False),
        sa.Column('open_from', sa.Date(), nullable=True),
        sa.Column('zip', sa.Unicode(8), nullable=False),
        sa.Column('business_run_from', sa.Date(), nullable=True),
        sa.Column('open_at', sa.Time(), nullable=False, server_default=text(u"'00:00:00'")),
        sa.Column('close_at', sa.Time(), nullable=False, server_default=text(u"'00:00:00'")),
        sa.Column('business_hours', sa.Integer(), nullable=False, server_default=text(u"1440")),
        sa.Column('opens_24hours', sa.Boolean(), nullable=False, server_default=text(u"TRUE")),
        sa.Column('closest_station', sa.Unicode(41), nullable=False, server_default=text(u"''")),
        sa.Column('liquor_available', sa.Boolean(), nullable=False, server_default=text(u"FALSE")),
        sa.Column('cigarettes_available', sa.Boolean(), nullable=False, server_default=text(u"FALSE")),
        sa.Column('business_run_until', sa.Date(), nullable=True),
        sa.Column('open_until', sa.Date(), nullable=True),
        sa.Column('business_paused_at', sa.Date(), nullable=True),
        sa.Column('business_continued_at', sa.Date(), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=8, scale=6), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('atm_available', sa.Boolean(), nullable=False, server_default=text(u"FALSE")),
        sa.Column('atm_available_from', sa.Date(), nullable=True),
        sa.Column('atm_available_until', sa.Date(), nullable=True),
        sa.Column('mmk_available', sa.Boolean(), nullable=False, server_default=text(u"FALSE")),
        sa.Column('mmk_available_from', sa.Date(), nullable=True),
        sa.Column('mmk_available_until', sa.Date(), nullable=True),
        sa.Column('renewal_start_at', sa.Date(), nullable=True),
        sa.Column('renewal_end_at', sa.Date(), nullable=True),
        sa.Column('business_status', sa.Integer, nullable=False, server_default=text(u"0")),
        sa.Column('paused', sa.Boolean(), nullable=False, server_default=text(u"FALSE")),
        sa.Column('deleted', sa.Boolean(), nullable=False, server_default=text(u"FALSE")),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False)
        )
    op.create_table(
        'FamiPortReceipt',
        sa.Column('id', Identifier, autoincrement=True),
        sa.Column('barcode_no', sa.Unicode(255), nullable=False),  # ファミポート側で使用するバーコード番号 barCodeNo
        sa.Column('exchange_number', sa.String(13), nullable=False),
        sa.Column('famiport_order_id', Identifier, sa.ForeignKey('FamiPortOrder.id'), nullable=False),
        sa.Column('shop_code', sa.Unicode(7), sa.ForeignKey('FamiPortShop.code'), nullable=False),
        sa.Column('inquired_at', sa.DateTime(), nullable=True),  # 予約照会が行われた日時
        sa.Column('payment_request_received_at', sa.DateTime(), nullable=True),  # 支払/発券要求が行われた日時
        sa.Column('customer_request_received_at', sa.DateTime(), nullable=True),  # 顧客情報照会が行われた日時
        sa.Column('completed_at', sa.DateTime(), nullable=True),  # 完了処理が行われた日時
        sa.Column('void_at', sa.DateTime(), nullable=True),  # 30分voidによって無効化された日時
        sa.Column('rescued_at', sa.DateTime(), nullable=True),  # 90分救済措置にて救済された時刻
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    op.drop_table('FamiPortReceipt')
    op.drop_table('FamiPortShop')
    op.drop_table('FamiPortRefundEntryResponse')
    op.drop_table('FamiPortTicketResponse')
    op.drop_table('FamiPortCustomerInformationResponse')
    op.drop_table('FamiPortInformationResponse')
    op.drop_table('FamiPortPaymentTicketingCancelResponse')
    op.drop_table('FamiPortPaymentTicketingCompletionResponse')
    op.drop_table('FamiPortPaymentTicketingResponse')
    op.drop_table('FamiPortReservationInquiryResponse')
    op.drop_table('FamiPortRefundEntryRequest')
    op.drop_table('FamiPortCustomerInformationRequest')
    op.drop_table('FamiPortInformationRequest')
    op.drop_table('FamiPortPaymentTicketingCancelRequest')
    op.drop_table('FamiPortPaymentTicketingCompletionRequest')
    op.drop_table('FamiPortPaymentTicketingRequest')
    op.drop_table('FamiPortReservationInquiryRequest')
    op.drop_table('FamiPortInformationMessage')
    op.drop_table('FamiPortRefundEntry')
    op.drop_table('FamiPortRefund')
    op.drop_table('FamiPortTicket')
    op.drop_table('FamiPortOrder')
    op.drop_table('FamiPortSalesSegment')
    op.drop_table('FamiPortPerformance')
    op.drop_table('FamiPortEvent')
    op.drop_table('FamiPortVenue')
    op.drop_table('FamiPortGenre2')
    op.drop_table('FamiPortGenre1')
    op.drop_table('FamiPortClient')
    op.drop_table('FamiPortPlayguide')
    op.drop_table('FamiPortReserveNumberSequence')
    op.drop_table('FamiPortExchangeTicketNoSequence')
    op.drop_table('FamiPortOrderTicketNoSequence')
    op.drop_table('FamiPortOrderIdentifierSequence')
    op.drop_table('FamiPortBarcodeNoSequence')
