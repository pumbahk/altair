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
    op.add_column('FamiPortOrder', sa.Column('barcode_no', sa.String(255), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('playguide_id', sa.String(255), nullable=False, default='', server_default=''))
    op.add_column('FamiPortOrder', sa.Column('total_amount', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('ticket_payment', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('system_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('ticketing_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('koen_date', sa.DateTime, nullable=False))
    op.add_column('FamiPortOrder', sa.Column('kogyo_name', sa.Unicode(40), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('ticket_total_count', sa.Integer, nullable=False))
    op.add_column('FamiPortOrder', sa.Column('ticket_count', sa.Integer, nullable=False))
    op.add_column('FamiPortOrder', sa.Column('name_input', sa.Integer, nullable=False, server_default=text('0')))
    op.add_column('FamiPortOrder', sa.Column('phone_input', sa.Integer, nullable=False, server_default=text('0')))
    op.add_column('FamiPortOrder', sa.Column('phone_number', sa.Unicode(12), nullable=False, server_default=text('0')))


def downgrade():
    op.drop_column('FamiPortOrder', 'name')
    op.drop_column('FamiPortOrder', 'koen_date')
    op.drop_column('FamiPortOrder', 'kogyo_name')
    op.drop_column('FamiPortOrder', 'total_amount')
    op.drop_column('FamiPortOrder', 'ticket_payment')
    op.drop_column('FamiPortOrder', 'system_fee')
    op.drop_column('FamiPortOrder', 'ticketing_fee')
    op.drop_column('FamiPortOrder', 'ticket_count')
    op.drop_column('FamiPortOrder', 'barcode_no')
    op.drop_column('FamiPortOrder', 'playguide_id')
    op.drop_column('FamiPortOrder', 'ticket_total_count')
    op.drop_column('FamiPortOrder', 'name_input')
    op.drop_column('FamiPortOrder', 'phone_input')
    op.drop_column('FamiPortOrder', 'phone_number')
