# -*- coding: utf-8 -*-
"""create famiport request models

Revision ID: 80dacb65b48
Revises: 384d80eaee31
Create Date: 2015-05-18 18:57:43.862066

"""

# revision identifiers, used by Alembic.
revision = '80dacb65b48'
down_revision = '384d80eaee31'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'FamiPortReservationInquiryRequest',
        sa.Column('id', Identifier),
        sa.Column('storeCode', sa.String(255), nullable=False),  # 店舗コード
        sa.Column('ticketingDate', sa.String(255), nullable=False),  # 利用日時
        sa.Column('reserveNumber', sa.String(255), nullable=False),  # 予約番号
        sa.Column('authNumber', sa.String(255), nullable=False),  # 認証番号
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.PrimaryKeyConstraint('id'),
        )

    op.create_table(
        'FamiPortPaymentTicketingRequest',
        sa.Column('id', Identifier),
        sa.Column('storeCode', sa.String(255), nullable=False),  # 店舗コード
        sa.Column('mmkNo', sa.String(255), nullable=False),  # 発券ファミポート番号
        sa.Column('ticketingDate', sa.String(255), nullable=False),  # 利用日時
        sa.Column('sequenceNo', sa.String(255), nullable=False),  # 処理通番
        sa.Column('playGuideId', sa.String(255), nullable=False),  # クライアントID
        sa.Column('barCodeNo', sa.String(255), nullable=False),  # 支払番号
        sa.Column('customerName', sa.String(255), nullable=False),  # カナ氏名
        sa.Column('phoneNumber', sa.String(255), nullable=False),  # 電話番号
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingCompletionRequest',
        sa.Column('id', Identifier),
        sa.Column('storeCode', sa.String(255), nullable=False),  # 店舗コード
        sa.Column('mmkNo', sa.String(255), nullable=False),  # 発券ファミポート番号
        sa.Column('ticketingDate', sa.String(255), nullable=False),  # 利用日時
        sa.Column('sequenceNo', sa.String(255), nullable=False),  # 処理通番
        sa.Column('requestClass', sa.String(255), nullable=False),  # 要求区分 TODO Delete the field?
        sa.Column('barCodeNo', sa.String(255), nullable=False),  # 支払番号
        sa.Column('playGuideId', sa.String(255), nullable=False),  # クライアントID
        sa.Column('orderId', sa.String(255), nullable=False),  # 注文ID
        sa.Column('totalAmount', sa.String(255), nullable=False),  # 入金金額
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortPaymentTicketingCancelRequest',
        sa.Column('id', Identifier),
        sa.Column('storeCode', sa.String(255), nullable=False),  # 店舗コード
        sa.Column('mmkNo', sa.String(255), nullable=False),  # 発券ファミポート番号
        sa.Column('ticketingDate', sa.String(255), nullable=False),  # 利用日時
        sa.Column('sequenceNo', sa.String(255), nullable=False),  # 処理通番
        sa.Column('requestClass', sa.String(255), nullable=False),  # 要求区分 TODO Delete the field?
        sa.Column('barCodeNo', sa.String(255), nullable=False),  # 支払番号
        sa.Column('playGuideId', sa.String(255), nullable=False),  # クライアントID
        sa.Column('orderId', sa.String(255), nullable=False),  # 注文ID
        sa.Column('cancelCode', sa.String(255), nullable=False),  # 取消理由
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortInformationRequest',
        sa.Column('id', Identifier),
        sa.Column('infoKubun', sa.String(255), nullable=False),  # 案内種別
        sa.Column('storeCode', sa.String(255), nullable=False),  # 店舗コード
        sa.Column('kogyoCode', sa.String(255), nullable=False),  # 興行コード
        sa.Column('kogyoSubCode', sa.String(255), nullable=False),  # 興行サブコード
        sa.Column('koenCode', sa.String(255), nullable=False),  # 公演コード
        sa.Column('uketsukeCode', sa.String(255), nullable=False),  # 受付コード
        sa.Column('playGuideId', sa.String(255), nullable=False),  # クライアントID
        sa.Column('authCode', sa.String(255), nullable=False),  # 認証コード
        sa.Column('reserveNumber', sa.String(255), nullable=False),  # 予約照会番号
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortCustomerInformationRequest',
        sa.Column('id', Identifier),
        sa.Column('storeCode', sa.String(255), nullable=False),  # 店舗コード
        sa.Column('mmkNo', sa.String(255), nullable=False),  # 発券Famiポート番号
        sa.Column('ticketingDate', sa.String(255), nullable=False),  # 利用日時
        sa.Column('sequenceNo', sa.String(255), nullable=False),  # 処理通番
        sa.Column('requestClass', sa.String(255), nullable=False),  # 要求区分 TODO Delete the field?
        sa.Column('barCodeNo', sa.String(255), nullable=False),  # バーコード情報
        sa.Column('playGuideId', sa.String(255), nullable=False),  # クライアントID
        sa.Column('orderId', sa.String(255), nullable=False),  # 注文ID
        sa.Column('totalAmount', sa.String(255), nullable=False),  # 入金金額
        sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    op.drop_table('FamiPortReservationInquiryRequest')
    op.drop_table('FamiPortPaymentTicketingRequest')
    op.drop_table('FamiPortPaymentTicketingCompletionRequest')
    op.drop_table('FamiPortPaymentTicketingCancelRequest')
    op.drop_table('FamiPortInformationRequest')
    op.drop_table('FamiPortCustomerInformationRequest')
