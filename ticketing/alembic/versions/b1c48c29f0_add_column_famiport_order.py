# -*- coding: utf-8 -*-
"""add_column_famiport_order

Revision ID: b1c48c29f0
Revises: 80dacb65b48
Create Date: 2015-05-19 03:02:22.347561

"""

# revision identifiers, used by Alembic.
revision = 'b1c48c29f0'
down_revision = '80dacb65b48'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('FamiPortOrder', sa.Column('name', sa.Unicode(42), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('barCodeNo', sa.String(255), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('playGuideId', sa.String(255), nullable=False, default='', server_default=''))
    op.add_column('FamiPortOrder', sa.Column('totalAmount', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('ticketPayment', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('systemFee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('ticketingFee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('koenDate', sa.DateTime, nullable=False))
    op.add_column('FamiPortOrder', sa.Column('kogyoName', sa.Unicode(40), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('ticketTotalCount', sa.Integer, nullable=False))
    op.add_column('FamiPortOrder', sa.Column('ticketCount', sa.Integer, nullable=False))
    op.add_column('FamiPortOrder', sa.Column('nameInput', sa.Integer, nullable=False, server_default=text('0')))
    op.add_column('FamiPortOrder', sa.Column('phoneInput', sa.Integer, nullable=False, server_default=text('0')))
    op.add_column('FamiPortOrder', sa.Column('phoneNumber', sa.Unicode(12), nullable=False, server_default=text('0')))


def downgrade():
    op.drop_column('FamiPortOrder', 'name')
    op.drop_column('FamiPortOrder', 'koenDate')
    op.drop_column('FamiPortOrder', 'kogyoName')
    op.drop_column('FamiPortOrder', 'totalAmount')
    op.drop_column('FamiPortOrder', 'ticketPayment')
    op.drop_column('FamiPortOrder', 'systemFee')
    op.drop_column('FamiPortOrder', 'ticketingFee')
    op.drop_column('FamiPortOrder', 'ticketCount')
    op.drop_column('FamiPortOrder', 'barCodeNo')
    op.drop_column('FamiPortOrder', 'playGuideId')
    op.drop_column('FamiPortOrder', 'ticketTotalCount')
    op.drop_column('FamiPortOrder', 'nameInput')
    op.drop_column('FamiPortOrder', 'phoneInput')
    op.drop_column('FamiPortOrder', 'phoneNumber')
