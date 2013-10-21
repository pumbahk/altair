# -*- coding: utf-8 -*-

"""add bank transfer to PaymentMethodPlugin

Revision ID: 10e7c48c9b2e
Revises: 1b7e3b0480d2
Create Date: 2013-10-21 16:41:45.670750

"""

# revision identifiers, used by Alembic.
revision = '10e7c48c9b2e'
down_revision = '1b7e3b0480d2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute(u"INSERT INTO PaymentMethodPlugin (id, name) VALUES (5, '銀行振込')")

def downgrade():
    op.execute(u"DELETE FROM PaymentMethodPlugin WHERE id = 5")
