# -*- coding: utf-8 -*-
"""add_famiport_order_column_shortfall

Revision ID: 26ba9e176c32
Revises: 223da4169ae7
Create Date: 2015-05-25 19:57:20.910454

"""

# revision identifiers, used by Alembic.
revision = '26ba9e176c32'
down_revision = '223da4169ae7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text  # noqa
from sqlalchemy.sql import functions as sqlf  # noqa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('FamiPortOrder', sa.Column('famiport_order_identifier', sa.String(12), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('order_ticket_no', sa.String(13), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('exchange_ticket_no', sa.String(13), nullable=False))
    op.add_column('FamiPortOrder', sa.Column('reserve_number', sa.String(13), nullable=False))
    op.create_table(
        'FamiPortOrderIdentifierSequence',
        sa.Column('id', Identifier),
        sa.Column('value', sa.String(12), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortOrderTicketNoSequence',
        sa.Column('id', Identifier),
        sa.Column('value', sa.String(12), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortExchangeTicketNoSequence',
        sa.Column('id', Identifier),
        sa.Column('value', sa.String(12), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.PrimaryKeyConstraint('id'),
        )
    op.create_table(
        'FamiPortReserveNumberSequence',
        sa.Column('id', Identifier),
        sa.Column('value', sa.String(12), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    op.drop_column('FamiPortOrder', 'famiport_order_identifier')
    op.drop_column('FamiPortOrder', 'order_ticket_no')
    op.drop_column('FamiPortOrder', 'exchange_ticket_no')
    op.drop_column('FamiPortOrder', 'reserve_number')
    op.drop_table('FamiPortOrderIdentifierSequence')
    op.drop_table('FamiPortOrderTicketNoSequence')
    op.drop_table('FamiPortExchangeTicketNoSequence')
    op.drop_table('FamiPortReserveNumberSequence')
