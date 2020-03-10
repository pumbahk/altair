# -*- coding: utf-8 -*-

"""Insert new plugin PaymentGateway to PaymentMethodPlugin.

Revision ID: 25fdb9f6af4f
Revises: 3cd6601615a3
Create Date: 2019-04-26 10:43:18.113824

"""

# revision identifiers, used by Alembic.
revision = '25fdb9f6af4f'
down_revision = '3cd6601615a3'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.execute(u"INSERT INTO PaymentMethodPlugin (id, name) VALUES (7, 'クレジットカード決済(PaymentGW)')")


def downgrade():
    op.execute(u"DELETE FROM PaymentMethodPlugin WHERE id = 7")
