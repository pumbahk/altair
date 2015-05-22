# -*- coding: utf-8 -*-
"""famiport_response

Revision ID: 223da4169ae7
Revises: b1c48c29f0
Create Date: 2015-05-22 22:46:41.002430

"""

# revision identifiers, used by Alembic.
revision = '223da4169ae7'
down_revision = 'b1c48c29f0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text  # noqa
from sqlalchemy.sql import functions as sqlf  # noqa

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'FamiPortReservationInquiryResponse',
        sa.Column('id', Identifier),
        sa.Column('resultCode', sa.String(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('replyClass', sa.String(1), nullable=False, server_default=''),  # 応答結果区分
        sa.Column('replyCode', sa.String(2), nullable=False, server_default=''),  # 応答結果
        sa.Column('playGuideId', sa.Unicode(24), nullable=False, server_default=''),  # クライアントID
        sa.Column('barCodeNo', sa.String(13), nullable=False, server_default=''),  # チケットバーコード番号
        sa.Column('totalAmount', sa.String(8), nullable=False, server_default=''),  # 合計金額
        sa.Column('ticketPayment', sa.String(8), nullable=False, server_default=''),  # チケット料金
        sa.Column('systemFee', sa.String(8), nullable=False, server_default=''),  # システム利用料
        sa.Column('ticketingFee', sa.String(8), nullable=False, server_default=''),  # チケット料金
        sa.Column('ticketCountTotal', sa.String(8), nullable=False, server_default=''),  # チケット枚数
        sa.Column('ticketCount', sa.String(8), nullable=False, server_default=''),  # 本券購入枚数
        sa.Column('kogyoName', sa.Unicode(40), nullable=False, server_default=''),  # 興行名
        sa.Column('koenDate', sa.String(12), nullable=False, server_default=''),  # 公演日時
        sa.Column('name', sa.Unicode(42), nullable=False, server_default=''),  # お客様指名
        sa.Column('nameInput', sa.String(1), nullable=False, server_default=''),  # 氏名要求フラグ
        sa.Column('phoneInput', sa.String(1), nullable=False, server_default=''),  # 電話番号要求フラグ
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingResponse',
        sa.Column('id', Identifier),
        sa.Column('resultCode', sa.String(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('storeCode', sa.String(6), nullable=False, server_default=''),  # 店舗コード
        sa.Column('sequenceNo', sa.String(11), nullable=False, server_default=''),  # 処理通番
        sa.Column('barCodeNo', sa.String(13), nullable=False, server_default=''),  # 支払番号
        sa.Column('orderId', sa.String(12), nullable=False, server_default=''),  # 注文ID
        sa.Column('replyClass', sa.String(1), nullable=False, server_default=''),  # 応答結果区分
        sa.Column('replyCode', sa.String(2), nullable=False, server_default=''),  # 応答結果
        sa.Column('playGuideId', sa.Unicode(24), nullable=False, server_default=''),  # クライアントID
        sa.Column('playGuideName', sa.Unicode(50), nullable=False, server_default=''),  # クライアント漢字名称
        sa.Column('orderTicketNo', sa.String(13), nullable=False, server_default=''),  # 払込票番号
        sa.Column('exchangeTicketNo', sa.String(13), nullable=False, server_default=''),  # 引換票番号
        sa.Column('ticketingStart', sa.String(12), nullable=False, server_default=''),  # 発券開始日時
        sa.Column('ticketingEnd', sa.String(12), nullable=False, server_default=''),  # 発券期限日時
        sa.Column('totalAmount', sa.Unicode(8), nullable=False, server_default=''),  # 合計金額
        sa.Column('ticketPayment', sa.Unicode(8), nullable=False, server_default=''),  # チケット料金
        sa.Column('systemFee', sa.Unicode(8), nullable=False, server_default=''),  # システム利用料
        sa.Column('ticketingFee', sa.Unicode(8), nullable=False, server_default=''),  # 店頭発券手数料
        sa.Column('ticketCountTotal', sa.Unicode(2), nullable=False, server_default=''),  # チケット枚数
        sa.Column('ticketCount', sa.Unicode(2), nullable=False, server_default=''),  # 本券購入枚数
        sa.Column('kogyoName', sa.Unicode(40), nullable=False, server_default=''),  # 興行名
        sa.Column('koenDate', sa.String(12), nullable=False, server_default=''),  # 公演日時
        sa.Column('barCodeNo', sa.String(13), nullable=False, server_default=''),  # チケットバーコード番号
        sa.Column('ticketClass', sa.String(1), nullable=False, server_default=''),  # チケット区分
        sa.Column('templateCode', sa.String(10), nullable=False, server_default=''),  # テンプレートコード
        sa.Column('ticketData', sa.Unicode(4000), nullable=False, server_default=''),  # 券面データ
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingCompletionResponse',
        sa.Column('id', Identifier),
        sa.Column('resultCode', sa.String(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('storeCode', sa.String(6), nullable=False, server_default=''),  # 店舗コード
        sa.Column('sequenceNo', sa.String(11), nullable=False, server_default=''),  # 処理通番
        sa.Column('barCodeNo', sa.String(13), nullable=False, server_default=''),  # 支払番号
        sa.Column('orderId', sa.String(12), nullable=False, server_default=''),  # 注文ID
        sa.Column('replyCode', sa.String(2), nullable=False, server_default=''),  # 応答結果
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingCancelResponse',
        sa.Column('id', Identifier),
        sa.Column('resultCode', sa.String(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('storeCode', sa.String(6), nullable=False, server_default=''),  # 店舗コード
        sa.Column('sequenceNo', sa.String(11), nullable=False, server_default=''),  # 処理通番
        sa.Column('barCodeNo', sa.String(13), nullable=False, server_default=''),  # 支払番号
        sa.Column('orderId', sa.String(12), nullable=False, server_default=''),  # 注文ID
        sa.Column('replyCode', sa.String(2), nullable=False, server_default=''),  # 応答結果
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortInformationResponse',
        sa.Column('id', Identifier),
        sa.Column('resultCode', sa.String(2), nullable=False, server_default=''),  # 処理結果コード
        sa.Column('infoKubu', sa.String(1), nullable=False, server_default=''),  # 案内区分
        sa.Column('infoMessage', sa.Unicode(500), nullable=False, server_default=''),  # 案内文言
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortCustomerInformationResponse',
        sa.Column('id', Identifier),
        sa.Column('resultCode', sa.String(2), nullable=False, server_default=''),  # 処理結果
        sa.Column('replyCode', sa.String(2), nullable=False, server_default=''),  # 応答結果
        sa.Column('name', sa.Unicode(42), nullable=False, server_default=''),  # 氏名
        sa.Column('memberId', sa.Unicode(100), nullable=False, server_default=''),  # 会員ID
        sa.Column('address1', sa.Unicode(200), nullable=False, server_default=''),  # 住所1
        sa.Column('address2', sa.Unicode(200), nullable=False, server_default=''),  # 住所1
        sa.Column('identifyNo', sa.Unicode(16), nullable=False, server_default=''),  # 半券個人識別番号
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortTicket',
        sa.Column('id', Identifier),
        sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    op.drop_table('FamiPortReservationInquiryResponse')
    op.drop_table('FamiPortPaymentTicketingResponse')
    op.drop_table('FamiPortPaymentTicketingCompletionResponse')
    op.drop_table('FamiPortPaymentTicketingCancelResponse')
    op.drop_table('FamiPortInformationResponse')
    op.drop_table('FamiPortCustomerInformationResponse')
    op.drop_table('FamiPortTicket')
